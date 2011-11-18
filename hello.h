
#define MY_EXPORT_PRIVATE __attribute__ ((visibility ("default")))

extern int aGlobalVariableWithExtern;
void functionWhoseDeclIsInHeader();

extern "C" {
extern int aGlobalVariableWithExternInExternSee;
void functionWhoseDeclIsInExternSee();
}

extern "C" void functionWhoHasExternSee();

inline bool inlineFunction() { return true; }


namespace myns {
  class ToBeMarkedAsExported { // Should be markd as EXPORT
  public:
    ToBeMarkedAsExported() {}
    virtual ~ToBeMarkedAsExported();
    
    void MethodToBeExported(); // Should NOT marked since the parent is already marked.
    void MethodToBeHidden(); // Should NOT be marked... at least for now.
    void MethodToBeHiddenInline() {} // Should be marked marked as INLINE
  };

  class NotMarked {
  public:
    NotMarked() {}
    virtual ~NotMarked();

    void ButTheMethodIsMarkedToBeExported(); // Should be marked as EXPORT.
    void MethodHiddenAsUsual(); // Should NOT be marked.
    void MethodHiddenAsUsualInline() {} // Should NOT be marked
  };
}

// Forward declaration
class GlobalClass;
