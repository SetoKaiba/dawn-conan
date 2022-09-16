import os
import glob
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy
from conan.tools.scm import Git


class DawnConan(ConanFile):
    name = "dawn"
    # version = "0.1"

    # Optional metadata
    license = "Apache License, Version 2.0"
    author = "Seto seto@kaiba.net"
    url = "https://github.com/SetoKaiba/dawn-conan"
    description = "dawn"
    topics = ("conan", "dawn")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    # Sources are located in the same place as this recipe, copy them to the recipe
    # exports_sources = "CMakeLists.txt", "src/*", "include/*"

    @property
    def _standalone_gclient_file(self):
        return os.path.join("scripts", "standalone.gclient")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def source(self):
        git = Git(self)
        clone_args = ['--depth', '1', '--branch', f"chromium/{self.version}"]
        git.clone(url="https://dawn.googlesource.com/dawn",
                  args=clone_args, target=".")
        if self.settings.os == "Windows":
            cmd = f"copy {self._standalone_gclient_file} .gclient"
        else:
            cmd = f"cp {self._standalone_gclient_file} .gclient"
        self.run(cmd)
        cmd = "gclient sync"
        self.run(cmd)

    def generate(self):
        print(self.conf_info.get("tools.cmake.cmaketoolchain:generator"))
        tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={
            "CMAKE_CXX_FLAGS": "/utf-8"
        } if self.settings.os == "Windows" else None)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.h",
             os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.h",
             os.path.join(self.build_folder, "gen", "include"),
             os.path.join(self.package_folder, "include"))
        if self.settings.os == "Windows":
            copy(self, "*.lib", self.build_folder,
                 os.path.join(self.package_folder, "lib"), False)
        else:
            copy(self, "*.a", self.build_folder,
                 os.path.join(self.package_folder, "lib"), False)

    def package_info(self):
        li = [f for _, _, files in os.walk(os.path.join(self.package_folder, "lib"))
              for f in files if f.endswith(".lib" if self.settings.os == "Windows" else ".a")]
        self.cpp_info.libs = li
