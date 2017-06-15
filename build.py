import platform

from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="libpng:shared", pure_c=True)
    new_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if platform.system() == "Darwin" and settings["arch"] == "x86":
            continue
        new_builds.append((settings, options, env_vars, build_requires))

    builder.builds = new_builds
    builder.run()

