[![Build Status](https://travis-ci.org/lasote/conan-libpng.svg)](https://travis-ci.org/lasote/conan-libpng)

# conan-libpng

[Conan.io](https://conan.io) package for lib libpng library: http://www.libpng.org/pub/png/libpng.html

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/libpng/1.6.21/lasote/stable).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

## Upload packages to server

    $ conan upload libpng/1.6.21@lasote/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install libpng/1.6.21@lasote/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    libpng/1.6.21@lasote/stable

    [options]
    libpng:shared=true # false
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

