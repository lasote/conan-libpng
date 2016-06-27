from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download
from conans.tools import unzip, replace_in_file
from conans import CMake


class LibpngConan(ConanFile):
    name = "libpng"
    version = "1.6.23"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/lasote/conan-libpng"
    requires = "zlib/1.2.8@lasote/stable"
    license="Open source: http://www.libpng.org/pub/png/src/libpng-LICENSE.txt"
    
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
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)     
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            if self.options.fPIC:
                 env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            else:
                 env_line = env.command_line     
            if self.settings.os == "Macos":
                old_str = '-install_name \$rpath/\$soname'
                new_str = '-install_name \$soname'
                replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)
                     
            configure = "cd %s && %s ./configure" % (self.ZIP_FOLDER_NAME, env_line)
            self.output.warn(configure)
            self.run(configure)
            self.run("cd %s && %s make" % (self.ZIP_FOLDER_NAME, env_line))
        else:
            conan_magic_lines = '''project(libpng)
    cmake_minimum_required(VERSION 3.0)
    include(../conanbuildinfo.cmake)
    CONAN_BASIC_SETUP()
    '''
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "cmake_minimum_required(VERSION 2.8.3)", conan_magic_lines)
            replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(libpng C)", "")
            
            cmake = CMake(self.settings)
            shared_options = "-DPNG_SHARED=ON -DPNG_STATIC=OFF" if self.options.shared else "-DPNG_SHARED=OFF -DPNG_STATIC=ON"
            
            self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
            cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
            self.run('%s && cmake .. %s %s' % (cd_build, cmake.command_line, shared_options))
            self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))
                
    def package(self):
        """ Define your conan structure: headers, libs, bins and data. After building your
            project, this method is called to create a defined structure:
        """
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
