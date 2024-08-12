#include <nan.h>
#include <iostream>

void Hello(const Nan::FunctionCallbackInfo<v8::Value>& info) {
    std::cout << "Hello function called!" << std::endl; // Log to console
    info.GetReturnValue().Set(Nan::New("Hello, World!").ToLocalChecked());
}

void Init(v8::Local<v8::Object> exports, v8::Local<v8::Value> module, v8::Local<v8::Context> context) {
    exports->Set(context,
                 Nan::New("hello").ToLocalChecked(),
                 Nan::New<v8::FunctionTemplate>(Hello)->GetFunction(context).ToLocalChecked());
}

NODE_MODULE_CONTEXT_AWARE(addon, Init)

