//===- PrintFunctionNames.cpp ---------------------------------------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file is based on tools/clang/examples/PrintFunctionNames/PrintFunctionNames.cpp
// 
//===----------------------------------------------------------------------===//

#include "clang/Frontend/FrontendPluginRegistry.h"
#include "clang/Basic/SourceManager.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/AST.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/AST/Mangle.h"
#include "clang/Frontend/CompilerInstance.h" 
#include "llvm/Support/raw_ostream.h"
using namespace clang;

namespace {

class ListSymbolsVisitor : public RecursiveASTVisitor<ListSymbolsVisitor> {
public:
    explicit ListSymbolsVisitor(CompilerInstance* ci, llvm::raw_fd_ostream* out)
        : m_ci(ci)
        , m_out(out)
        , m_mangle(ci->getASTContext().createMangleContext())
    {
    }

    bool VisitFunctionDecl(FunctionDecl* decl);
    bool VisitRecordDecl(RecordDecl* decl);
    bool VisitVarDecl(VarDecl* decl);

    CompilerInstance* ci() const { return m_ci; }
    llvm::raw_ostream& out() const { return m_out ? *m_out : llvm::outs() ; }
    MangleContext* mangle() const { return m_mangle; }

private:
    bool isFromSystem(const PresumedLoc& loc) const;
    void printLocation(const PresumedLoc& loc);
    void printOptionsFor(const std::vector<std::string>& options) const;
    std::vector<std::string> makeOptionsFor(FunctionDecl* decl) const;
    CompilerInstance* m_ci;
    llvm::raw_fd_ostream* m_out;
    MangleContext* m_mangle;
};

static const std::string& kindNameFor(FunctionDecl* decl)
{
    const static std::string kCXXConstructorDecl("CXXConstructorDecl");
    const static std::string kCXXDestructorDecl("CXXDestructorDecl");
    const static std::string kCXXMethodDecl("CXXMethodDecl");
    const static std::string kFunctionDecl("FunctionDecl");
    
    if (isa<CXXConstructorDecl>(decl))
        return kCXXConstructorDecl;
    if (isa<CXXDestructorDecl>(decl))
        return kCXXDestructorDecl;
    if (isa<CXXMethodDecl>(decl))
        return kCXXMethodDecl;
    return kFunctionDecl;
}

std::vector<std::string> ListSymbolsVisitor::makeOptionsFor(FunctionDecl* decl) const
{
    std::vector<std::string> opts;
    if (decl->isThisDeclarationADefinition())
        opts.push_back("definition");
    // Why hasBody()? I don't know. See getLVForClassMember() in Decl.cpp
    if (decl->isInlined() && decl->hasBody()) 
        opts.push_back("inlined");
    return opts;
}

void ListSymbolsVisitor::printOptionsFor(const std::vector<std::string>& options) const
{
    out() << " \"options\": [";
    for (size_t oi = 0; oi < options.size(); ++oi) {
        out() << "\"" << options[oi] << "\"" ;
        if (oi + 1 != options.size())
            out() << ", ";
    }
    out() << "],\n";
}

bool ListSymbolsVisitor::VisitFunctionDecl(FunctionDecl* decl)
{
    PresumedLoc presumedLoc = m_ci->getSourceManager().getPresumedLoc(decl->getLocation());
    if (isFromSystem(presumedLoc))
        return true;

    // Should distinguish method/static method?
    out() << "{\n";
    out() << " \"kind\": \"" << kindNameFor(decl) << "\", \n";
    out() << " \"name\": " << "\"" <<  decl->getNameAsString() << "\",\n";
    if (const RecordDecl* parent = dyn_cast<RecordDecl>(decl->getDeclContext()))
        out() << " \"parent\": \"" << parent->getNameAsString() << "\",\n";

    printOptionsFor(makeOptionsFor(decl));
    printLocation(presumedLoc);

    out() << " \"symbols\": [";

    if (isa<CXXConstructorDecl>(decl)) {
        out() << "\"";
        mangle()->mangleCXXCtor(static_cast<CXXConstructorDecl*>(decl), Ctor_Complete, out());
        out() << "\",\"";
        mangle()->mangleCXXCtor(static_cast<CXXConstructorDecl*>(decl), Ctor_Base, out());
        out() << "\",\"";
        mangle()->mangleCXXCtor(static_cast<CXXConstructorDecl*>(decl), Ctor_CompleteAllocating, out());
        out() << "\"";
    } else if (isa<CXXDestructorDecl>(decl)) {
        // XXX: Need mangleCXXDtorThunk?
        out() << "\"";
        mangle()->mangleCXXDtor(static_cast<CXXDestructorDecl*>(decl), Dtor_Deleting, out());
        out() << "\",\"";
        mangle()->mangleCXXDtor(static_cast<CXXDestructorDecl*>(decl), Dtor_Complete, out());
        out() << "\",\"";
        mangle()->mangleCXXDtor(static_cast<CXXDestructorDecl*>(decl), Dtor_Base, out());
        out() << "\"";
    } else {
        out() << "\"";
        // XXX: Maybe we should care about pure C code which won't have isExternCContext() but has C names.
        // XXX: Can use shouldMangleDeclName() ?
        if (mangle()->shouldMangleDeclName(decl))
            mangle()->mangleName(decl, out());
        else
            out() << decl->getNameAsString();
        out() << "\"";
    }

    out() << " ]\n},\n";

    return true;
}

bool ListSymbolsVisitor::VisitRecordDecl(RecordDecl* decl)
{
    // class declaration cannot have attributes.
    if (!decl->isThisDeclarationADefinition())
        return true;

    PresumedLoc presumedLoc = m_ci->getSourceManager().getPresumedLoc(decl->getLocation());
    if (isFromSystem(presumedLoc))
        return true;

    out() << "{\n";
    out() << " \"kind\": \"RecordDecl\", \n";
    out() << " \"name\": " << "\"" <<  decl->getNameAsString() << "\",\n";

    std::vector<std::string> options;
    if (decl->isThisDeclarationADefinition())
        options.push_back("definition");
    printOptionsFor(options);
    printLocation(presumedLoc);

    out() << " \"symbols\": [";

    if (isa<CXXRecordDecl>(decl)) {
        out() << "\"";
        mangle()->mangleCXXVTable(static_cast<CXXRecordDecl*>(decl), out());
        out() << "\",\"";
        mangle()->mangleCXXVTT(static_cast<CXXRecordDecl*>(decl), out());
        out() << "\"";
    }

    out() << " ]\n},\n";
    return true;
}

bool ListSymbolsVisitor::VisitVarDecl(VarDecl* decl)
{
    PresumedLoc presumedLoc = m_ci->getSourceManager().getPresumedLoc(decl->getLocation());
    if (isFromSystem(presumedLoc))
        return true;
    if (decl->getNameAsString().empty())
        return true;

    out() << "{\n";
    out() << " \"kind\": \"VarDecl\", \n";
    out() << " \"name\": " << "\"" <<  decl->getNameAsString() << "\",\n";

    std::vector<std::string> options;
    if (decl->isThisDeclarationADefinition())
        options.push_back("definition");
    printOptionsFor(options);
    printLocation(presumedLoc);

    out() << " \"symbols\": [";
    out() << "\"";
    if (mangle()->shouldMangleDeclName(decl)) {
        mangle()->mangleName(decl, out());
        //mangle()->mangleReferenceTemporary(decl, out());
    } else 
        out() << decl->getNameAsString();
    out() << "\"";
    out() << " ]\n},\n";

    return true;
}

bool ListSymbolsVisitor::isFromSystem(const PresumedLoc& loc) const
{
    return (0 == std::string(loc.getFilename()).find("/usr/") || (0 == strcmp(loc.getFilename(), "<built-in>")));
}

void ListSymbolsVisitor::printLocation(const PresumedLoc& loc)
{
    out() << " \"location\": [\"" << loc.getFilename() << "\", " << loc.getLine() << ", " << loc.getColumn() << "],\n";
}

class ListSymbolsConsumer : public ASTConsumer {
public:
    ListSymbolsConsumer(CompilerInstance* ci, const std::string& filename)
        : m_file(filename.c_str(), m_fileError)
        , m_visitor(ci, filename.empty() ? 0 : &m_file)
    {
    }

    virtual void HandleTopLevelDecl(DeclGroupRef DG)
    {
        for (DeclGroupRef::iterator i = DG.begin(), e = DG.end(); i != e; ++i) {
            const Decl *D = *i;
            if (const NamedDecl *ND = dyn_cast<NamedDecl>(D))
                m_visitor.TraverseDecl(const_cast<NamedDecl*>(ND));
            else if (const LinkageSpecDecl* linkage = dyn_cast<LinkageSpecDecl>(D)) {
                for (DeclContext::decl_iterator li = linkage->decls_begin(); li != linkage->decls_end(); ++li) {
                    if (const NamedDecl *ND = dyn_cast<NamedDecl>(*li))
                        m_visitor.TraverseDecl(const_cast<NamedDecl*>(ND));
                }
            }
        }
    }

    virtual void Initialize(ASTContext &Context)
    {
        SourceManager& sm = m_visitor.ci()->getSourceManager();
        PresumedLoc loc = sm.getPresumedLoc(sm.getLocForStartOfFile(sm.getMainFileID()));
        m_visitor.out() << "{ \"file\": \"" << loc.getFilename() << "\",\n";
        m_visitor.out() << "  \"locations\": \n";
        m_visitor.out() << "[\n";
    }

    virtual void HandleTranslationUnit(ASTContext &Ctx)
    {
        m_visitor.out() << "null\n";
        m_visitor.out() << "]}\n";
    }

private:
    std::string m_fileError;
    llvm::raw_fd_ostream m_file;
    ListSymbolsVisitor m_visitor;
};
  
class ListSymbolsAction : public PluginASTAction {
protected:
    ASTConsumer *CreateASTConsumer(CompilerInstance &CI, llvm::StringRef) {
        return new ListSymbolsConsumer(&CI, m_filename);
    }

    bool ParseArgs(const CompilerInstance &CI,
                   const std::vector<std::string>& args) {
        if (args.empty())
            return true;
            
        m_filename = args[0];
        return true;
    }

private:
    std::string m_filename;
};

}

static FrontendPluginRegistry::Add<ListSymbolsAction>
X("list-exp", "list exportables");
