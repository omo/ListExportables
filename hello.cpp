
#include <vector>
#include "hello.h"

void functionNoForwardDecl()
{
}

int functionWithForwardDecl();

extern int aGlobalVariableWithTwoExterns;
extern int aGlobalVariableWithTwoExterns;

class GlobalClass {
public:
  GlobalClass() {}
  ~GlobalClass();
};

class ClassWithVirtual {
public:
  ClassWithVirtual() {}
  virtual ~ClassWithVirtual();
};

namespace ns {
  class NamespacedClass {
  public:
    void inlineMethod() {}
    static void inlineStaticMethod() {}
  private:
    int message_id;
  };

  int aGlobalVariableInsideNamespace;
}

class ClassWithStaticVar {
public:
  static int s_staticVar;
};

int ClassWithStaticVar::s_staticVar;

int functionWithForwardDecl()
{
  return 0;
}

GlobalClass::~GlobalClass()
{
}

ClassWithVirtual::~ClassWithVirtual()
{
}

void functionWhoseDeclIsInHeader()
{
}

void functionWhoseDeclIsInExternSee()
{
}

void functionWhoHasExternSee()
{
}

int aGlobalVariable;
int aGlobalVariableWithExtern;
int aGlobalVariableWithTwoExterns;
int aGlobalVariableWithExternInExternSee;

class SyntaxPlayground {
  MY_EXPORT_PRIVATE static int staticVar;
};

int SyntaxPlayground::staticVar = 0;

extern "C" const int jscore_fastmalloc_introspection = 0;


namespace myns {

ToBeMarkedAsExported::~ToBeMarkedAsExported()
{
}

#if 0
void ToBeMarkedAsExported::MethodToBeExported()
{
}
#endif

void ToBeMarkedAsExported::MethodToBeHidden()
{
}

NotMarked::~NotMarked()
{
}

void NotMarked::ButTheMethodIsMarkedToBeExported()
{
}

}

