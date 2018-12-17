import ops
import iopc

TARBALL_FILE="mesa-18.0.1.tar.xz"
TARBALL_DIR="mesa-18.0.1"
INSTALL_DIR="mesa-bin"
pkg_path = ""
output_dir = ""
tarball_pkg = ""
tarball_dir = ""
install_dir = ""
install_tmp_dir = ""
cc_host = ""
tmp_include_dir = ""
dst_include_dir = ""
dst_lib_dir = ""
dst_usr_local_lib_dir = ""
PKG_WAYLAND="wayland"

def set_global(args):
    global pkg_path
    global output_dir
    global tarball_pkg
    global install_dir
    global install_tmp_dir
    global tarball_dir
    global cc_host
    global tmp_include_dir
    global dst_include_dir
    global dst_lib_dir
    global dst_usr_local_lib_dir
    global src_pkgconfig_dir
    global dst_pkgconfig_dir
    pkg_path = args["pkg_path"]
    output_dir = args["output_path"]
    tarball_pkg = ops.path_join(pkg_path, TARBALL_FILE)
    install_dir = ops.path_join(output_dir, INSTALL_DIR)
    install_tmp_dir = ops.path_join(output_dir, INSTALL_DIR + "-tmp")
    tarball_dir = ops.path_join(output_dir, TARBALL_DIR)
    cc_host_str = ops.getEnv("CROSS_COMPILE")
    cc_host = cc_host_str[:len(cc_host_str) - 1]
    tmp_include_dir = ops.path_join(output_dir, ops.path_join("include",args["pkg_name"]))
    dst_include_dir = ops.path_join("include",args["pkg_name"])
    dst_lib_dir = ops.path_join(install_dir, "lib")
    dst_usr_local_lib_dir = ops.path_join(install_dir, "usr/local/lib")
    src_pkgconfig_dir = ops.path_join(pkg_path, "pkgconfig")
    dst_pkgconfig_dir = ops.path_join(install_dir, "pkgconfig")

def MAIN_ENV(args):
    set_global(args)

    ops.exportEnv(ops.setEnv("CC", ops.getEnv("CROSS_COMPILE") + "gcc"))
    ops.exportEnv(ops.setEnv("CXX", ops.getEnv("CROSS_COMPILE") + "g++"))
    ops.exportEnv(ops.setEnv("CROSS", ops.getEnv("CROSS_COMPILE")))
    ops.exportEnv(ops.setEnv("DESTDIR", install_tmp_dir))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_LIBDIR", ops.path_join(iopc.getSdkPath(), "pkgconfig")))
    #ops.exportEnv(ops.setEnv("PKG_CONFIG_SYSROOT_DIR", iopc.getSdkPath()))

    return False

def MAIN_EXTRACT(args):
    set_global(args)

    ops.unTarXz(tarball_pkg, output_dir)
    #ops.copyto(ops.path_join(pkg_path, "finit.conf"), output_dir)

    return True

def MAIN_PATCH(args, patch_group_name):
    set_global(args)
    for patch in iopc.get_patch_list(pkg_path, patch_group_name):
        if iopc.apply_patch(tarball_dir, patch):
            continue
        else:
            sys.exit(1)

    return True

def MAIN_CONFIGURE(args):
    set_global(args)

    cflags = iopc.get_includes()
    libs = iopc.get_libs()

    extra_conf = []
    extra_conf.append("--host=" + cc_host)
    extra_conf.append("--disable-selinux")
    extra_conf.append("--enable-opengl")
    extra_conf.append("--disable-gles1")
    extra_conf.append("--enable-gles2")
    extra_conf.append("--disable-dri3")
    extra_conf.append("--disable-lmsensors")
    extra_conf.append("--disable-glx")
    extra_conf.append("--disable-xa")
    extra_conf.append("--enable-dri")
    extra_conf.append("--disable-va")
    extra_conf.append("--enable-egl")
    extra_conf.append("--enable-driglx-direct")
    extra_conf.append("--enable-glx-tls")
    extra_conf.append("--enable-texture-float")
    if iopc.is_selected_package(PKG_WAYLAND):
        extra_conf.append("-with-platforms=drm,wayland")
        extra_conf.append('WAYLAND_CLIENT_CFLAGS=' + cflags)
        extra_conf.append('WAYLAND_CLIENT_LIBS=' + libs)
        extra_conf.append('WAYLAND_SERVER_CFLAGS=' + cflags)
        extra_conf.append('WAYLAND_SERVER_LIBS=' + libs)
    else:
        extra_conf.append("-with-platforms=drm,surfaceless")
    extra_conf.append("--with-gallium-drivers=svga,swrast")
    #extra_conf.append("--with-gallium-drivers=nouveau,swrast,radeonsi")
    extra_conf.append("--enable-gbm") 
    #extra_conf.append("--enable-osmesa")
    extra_conf.append("--enable-gallium-osmesa")
    extra_conf.append("--without-vulkan-drivers")
    #extra_conf.append("--with-dri-drivers=swrast")
    extra_conf.append("--with-dri-drivers=swrast,i915,i965,nouveau")
    extra_conf.append("--enable-shared-glapi")
    extra_conf.append("--enable-gallium-tests")

    extra_conf.append('ZLIB_CFLAGS=' + cflags)
    extra_conf.append('ZLIB_LIBS=' + libs)
    extra_conf.append('EXPAT_CFLAGS=' + cflags)
    extra_conf.append('EXPAT_LIBS=' + libs)
    extra_conf.append('LIBDRM_CFLAGS=' + cflags)
    extra_conf.append('LIBDRM_LIBS=' + libs)
    extra_conf.append('I915_CFLAGS=' + cflags)
    extra_conf.append('I915_LIBS=' + libs)
    extra_conf.append('NOUVEAU_CFLAGS=' + cflags)
    extra_conf.append('NOUVEAU_LIBS=' + libs)
    extra_conf.append('NVVIEUX_CFLAGS=' + cflags)
    extra_conf.append('NVVIEUX_LIBS=' + libs)

    iopc.configure(tarball_dir, extra_conf)

    return True

def MAIN_BUILD(args):
    set_global(args)

    ops.mkdir(install_dir)
    ops.mkdir(install_tmp_dir)
    iopc.make(tarball_dir)
    iopc.make_install(tarball_dir)

    ops.mkdir(install_dir)
    ops.mkdir(dst_lib_dir)
    ops.mkdir(dst_usr_local_lib_dir)
    libegl = "libEGL.so.1.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libegl), dst_lib_dir)
    ops.ln(dst_lib_dir, libegl, "libEGL.so.1.0")
    ops.ln(dst_lib_dir, libegl, "libEGL.so.1")
    ops.ln(dst_lib_dir, libegl, "libEGL.so")

    libglesv2 = "libGLESv2.so.2.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libglesv2), dst_lib_dir)
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so.2.0")
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so.2")
    ops.ln(dst_lib_dir, libglesv2, "libGLESv2.so")

    libgbm = "libgbm.so.1.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libgbm), dst_lib_dir)
    ops.ln(dst_lib_dir, libgbm, "libgbm.so.1.0")
    ops.ln(dst_lib_dir, libgbm, "libgbm.so.1")
    ops.ln(dst_lib_dir, libgbm, "libgbm.so")

    libglapi = "libglapi.so.0.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libglapi), dst_lib_dir)
    ops.ln(dst_lib_dir, libglapi, "libglapi.so.0.0")
    ops.ln(dst_lib_dir, libglapi, "libglapi.so.0")
    ops.ln(dst_lib_dir, libglapi, "libglapi.so")

    libosmesa = "libOSMesa.so.8.0.0"
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libosmesa), dst_lib_dir)
    ops.ln(dst_lib_dir, libosmesa, "libOSMesa.so.8.0")
    ops.ln(dst_lib_dir, libosmesa, "libOSMesa.so.8")
    ops.ln(dst_lib_dir, libosmesa, "libOSMesa.so")

    if iopc.is_selected_package(PKG_WAYLAND):
        libwayland = "libwayland-egl.so.1.0.0"
        ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/" + libwayland), dst_lib_dir)
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so.1.0")
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so.1")
        ops.ln(dst_lib_dir, libwayland, "libwayland-egl.so")

    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/lib/dri"), dst_usr_local_lib_dir)

    ops.mkdir(tmp_include_dir)
    ops.copyto(ops.path_join(install_tmp_dir, "usr/local/include/."), tmp_include_dir)

    ops.mkdir(dst_pkgconfig_dir)
    ops.copyto(ops.path_join(src_pkgconfig_dir, '.'), dst_pkgconfig_dir)

    return True

def MAIN_INSTALL(args):
    set_global(args)

    iopc.installBin(args["pkg_name"], ops.path_join(ops.path_join(install_dir, "lib"), "."), "lib")
    iopc.installBin(args["pkg_name"], ops.path_join(dst_usr_local_lib_dir, "."), "usr/local/lib")
    iopc.installBin(args["pkg_name"], ops.path_join(tmp_include_dir, "."), dst_include_dir)
    iopc.installBin(args["pkg_name"], ops.path_join(dst_pkgconfig_dir, '.'), "pkgconfig")

    return False

def MAIN_SDKENV(args):
    set_global(args)

    cflags = ""
    cflags += " -I" + ops.path_join(iopc.getSdkPath(), 'usr/include/' + args["pkg_name"])
    cflags += " -DMESA_EGL_NO_X11_HEADERS"
    iopc.add_includes(cflags)

    libs = ""
    libs += " -lEGL -lGLESv2 -lgbm -lglapi -lOSMesa -lwayland-egl"
    iopc.add_libs(libs)

    return False

def MAIN_CLEAN_BUILD(args):
    set_global(args)

    return False

def MAIN(args):
    set_global(args)

