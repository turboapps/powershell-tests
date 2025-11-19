#include <napi.h>
#include <iostream>

Napi::String HelloWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::cout << "Hello function called!" << std::endl; // logs to console
    return Napi::String::New(env, "Hello, World!");
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "hello"),
                Napi::Function::New(env, HelloWrapped));
    return exports;
}

NODE_API_MODULE(addon, Init)
