from conans import ConanFile, tools
import os
from conans.tools import download
from conans.tools import unzip, replace_in_file
from conans import CMake, AutoToolsBuildEnvironment


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.23"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/lasote/conan-libpng"
    requires = "zlib/1.2.11@lasote/stable"
    license = "Open source: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    exports = "FindPNG.cmake"
    description = "libpng is the official PNG reference library. It supports almost all PNG features, is extensible,"" \
    "" and has been extensively tested for over 20 years."
    
    def config(self):
        try: # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx 
        except: 
            pass
        
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
        
    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        try:
            download("https://sourceforge.net/projects/libpng/files/libpng16/%s/%s" % (self.version, zip_name), zip_name)
        except Exception:
            download("https://sourceforge.net/projects/libpng/files/libpng16/older-releases/%s/%s" % (self.version, zip_name), zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """

        if self.settings.os == "Linux" or self.settings.os == "Macos":

            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = self.options.fPIC

            with tools.environment_append(env_build.vars):
                with tools.chdir(self.ZIP_FOLDER_NAME):
                    if self.settings.os == "Macos":
                        replace_in_file("./configure", '-install_name \$rpath/\$soname', '-install_name \$soname')
                    self.run("./configure")
                    self.run("make")
        else:
            conan_magic_lines = '''project(libpng)
cmake_minimum_required(VERSION 3.0)
include(../conanbuildinfo.cmake)
CONAN_BASIC_SETUP()
    '''
            with tools.chdir(self.ZIP_FOLDER_NAME):
                replace_in_file("CMakeLists.txt", "cmake_minimum_required(VERSION 2.8.3)", conan_magic_lines)
                replace_in_file("CMakeLists.txt", "project(libpng C)", "")

                cmake = CMake(self.settings)
                shared_options = "-DPNG_SHARED=ON -DPNG_STATIC=OFF" if self.options.shared else "-DPNG_SHARED=OFF -DPNG_STATIC=ON"

                self.run("mkdir _build")
                with tools.chdir("./_build"):
                    self.run('cmake .. %s %s' % (cmake.command_line, shared_options))
                    self.run("cmake --build . %s" % cmake.build_config)
                
    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
        # Copy findPNG.cmake to package
        self.copy("FindPNG.cmake", ".", ".")

        # Copy pc file
        self.copy("*.pc", dst="", keep_path=False)

        # Copying headers
        self.copy("*.h", "include", "%s" % (self.ZIP_FOLDER_NAME), keep_path=False)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.libs = ['libpng16']
            else:
                self.cpp_info.libs = ['libpng16_static']
            if self.settings.build_type == "Debug":
                self.cpp_info.libs[0] += "d"
        else:
            self.cpp_info.libs = ["png16"]
            if self.settings.os == "Linux":
                self.cpp_info.libs.append("m")
