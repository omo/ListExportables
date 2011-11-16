
#include <vector>
#include "hello.h"

void functionNoForwardDecl()
{
}

int functionWithForwardDecl();

class GlobalClass {
public:
  GlobalClass() {}
  ~GlobalClass();
};

class ClassVithVirtual {
public:
  ClassVithVirtual() {}
  virtual ~ClassVithVirtual();
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

ClassVithVirtual::~ClassVithVirtual()
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
int aGlobalVariableWithExternInExternSee;

class SyntaxPlayground {
  MY_EXPORT_PRIVATE static int staticVar;
};

int SyntaxPlayground::staticVar = 0;
