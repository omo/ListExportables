
extern int aGlobalVariableWithExtern;
void functionWhoseDeclIsInHeader();

extern "C" {
extern int aGlobalVariableWithExternInExternSee;
void functionWhoseDeclIsInExternSee();
}

extern "C" void functionWhoHasExternSee();
