
#define JSC_PRIVATE_EXPORT __attribute__ ((visibility ("default")))

extern int aGlobalVariableWithExtern;
void functionWhoseDeclIsInHeader();

extern "C" {
extern int aGlobalVariableWithExternInExternSee;
void functionWhoseDeclIsInExternSee();
}

extern "C" void functionWhoHasExternSee();

// Forward declaration
class GlobalClass;
