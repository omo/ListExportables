
#define MY_EXPORT_PRIVATE __attribute__ ((visibility ("default")))
#define MY_INLINE inline __attribute__ ((visibility ("hidden")))

extern int aGlobalVariableWithExtern;
void functionWhoseDeclIsInHeader();

extern "C" {
extern int aGlobalVariableWithExternInExternSee;
void functionWhoseDeclIsInExternSee();
}

extern "C" void functionWhoHasExternSee();

inline bool inlineFunction() { return true; }


namespace myns {
  class MY_EXPORT_PRIVATE ToBeMarkedAsExported { // Should be markd as EXPORT
  public:
    ToBeMarkedAsExported() {}
    virtual ~ToBeMarkedAsExported();
    
    void MethodToBeExported(); // Should NOT marked since the parent is already marked.
    void MethodToBeHidden(); // Should NOT be marked... at least for now.
    void MethodToBeHiddenInline() {} // Should be marked marked as INLINE
    void MethodToBeHiddenSeparateInline(); // Should be marked marked as INLINE
  };

  class NotMarked {
  public:
    NotMarked() {}
    virtual ~NotMarked();

    MY_EXPORT_PRIVATE void ButTheMethodIsMarkedToBeExported(); // Should be marked as EXPORT.
    void MethodHiddenAsUsual(); // Should NOT be marked.
    void MethodHiddenAsUsualInline() {} // Should NOT be marked
  };

#if 0
  inline void ToBeMarkedAsExported::MethodToBeHiddenSeparateInline()
  {
  }
#endif
}


namespace myns {
#if 1
  inline void ToBeMarkedAsExported::MethodToBeHiddenSeparateInline()
  {
  }
#endif
}


// Forward declaration
class GlobalClass;
