from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    mingw_configurations = [("4.9", "x86_64", "seh", "posix")]
    builder = ConanMultiPackager(username="lasote", mingw_configurations=mingw_configurations)
    builder.add_common_builds(shared_option_name="libpng:shared", pure_c=True)
    builder.run()

