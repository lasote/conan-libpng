import os
import platform

from conans import CMake, AutoToolsBuildEnvironment
from conans import ConanFile, tools


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.23"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/lasote/conan-libpng"
    license = "Open source: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    exports = "FindPNG.cmake"
    description = "libpng is the official PNG reference library. It supports almost all PNG features, is extensible,"" \
    "" and has been extensively tested for over 20 years."

    def requirements(self):
        self.requires.add("zlib/1.2.11@%s/stable" % self.user)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        del self.settings.compiler.libcxx
        
    def source(self):
        base_url = "https://sourceforge.net/projects/libpng/files/libpng16/"
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        try:
            tools.download("%s/%s/%s" % (base_url, self.version, zip_name), zip_name)
        except Exception:
            tools.download("%s/older-releases/%s/%s" % (base_url, self.version, zip_name), zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """

        if not tools.OSInfo().is_windows:
            self._build_configure()
        else:
            self._build_cmake()

    def _build_cmake(self):
        conan_magic_lines = '''project(libpng)
        cmake_minimum_required(VERSION 3.0)
        include(../conanbuildinfo.cmake)
        CONAN_BASIC_SETUP()
            '''
        with tools.chdir(self.ZIP_FOLDER_NAME):
            tools.replace_in_file("CMakeLists.txt", "cmake_minimum_required(VERSION 2.8.3)", conan_magic_lines)
            tools.replace_in_file("CMakeLists.txt", "project(libpng C)", "")
            if self.settings.os == "Android" and platform.system() == "Windows":
                tools.replace_in_file("CMakeLists.txt", "find_program(AWK NAMES gawk awk)", "")
            self.run("mkdir _build")
            with tools.chdir("./_build"):
                cmake = CMake(self)
                cmake.definitions["PNG_SHARED"] = "ON" if self.options.shared else "OFF"
                cmake.definitions["PNG_STATIC"] = "OFF" if self.options.shared else "ON"
                cmake.configure(source_dir="../", build_dir="./")
                cmake.build()

    def _build_configure(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC

        with tools.chdir(self.ZIP_FOLDER_NAME):
            if platform.system() == "Darwin":
                tools.replace_in_file("./configure", r'-install_name \$rpath/\$soname', r'-install_name \$soname')
            env_build.configure()
            env_build.make()

            tools.replace_in_file("libpng16.pc", "${prefix}/include/libpng16", "${prefix}/include")
            tools.replace_in_file("libpng.pc", "${prefix}/include/libpng16", "${prefix}/include")
            if not self.options.shared:
                tools.replace_in_file("libpng16.pc", "-lpng16", "-lpng16 -lm -lz")
                tools.replace_in_file("libpng.pc", "-lpng16", "-lpng16 -lm -lz")

    def package(self):
        # Copy findPNG.cmake to package
        self.copy("FindPNG.cmake", ".", ".")

        # Copy pc file
        if self.settings.os != "Android": # Broken symlink
            self.copy("*.pc", dst="", keep_path=False)

        # Copying headers
        self.copy("*png*.h", "include", self.ZIP_FOLDER_NAME, keep_path=True)
        self.copy("*.h", "include", os.path.join(self.ZIP_FOLDER_NAME, "contrib"), keep_path=True)

        # Copying static and dynamic libs
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                if self.options.shared:
                    self.copy(pattern="*.dll", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                    self.copy(pattern="*libpng.dll.a", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                    self.copy(pattern="*libpng16.dll.a", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                else:
                    self.copy(pattern="*libpng.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                    self.copy(pattern="*libpng16.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                if self.options.shared:
                    self.copy(pattern="*.dll", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                if self.settings.os == "Android":
                    self.copy(pattern="*.a", dst="lib", src=os.path.join(self.ZIP_FOLDER_NAME), keep_path=False)
                else:
                    self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "gcc":
                self.cpp_info.libs = ["png"]
            else:
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
