from fabric.api import sudo, cd
from fabric.operations import reboot
from fabric.contrib.files import exists, append


def _install_depends():
    sudo("apt-get update")
    sudo("apt-get upgrade -y")
    sudo("apt-get install -y linux-generic")
    sudo("apt-get install -y linux-image-generic-lts-trusty")
    reboot()

    sudo("apt-get install -y linux-headers-`uname -r`")

    sudo("apt-get install -y build-essential")
    sudo("apt-get install -y git")
    sudo("apt-get install -y wget curl")


def _unload_nouveau():
    lines = []
    lines.append("blacklist vga16fb")
    lines.append("blacklist nouveau")
    lines.append("blacklist rivafb")
    lines.append("blacklist nvidiafb")
    lines.append("blacklist rivatv")
    append("/etc/modprobe.d/blacklist.conf", lines, use_sudo=True)

    sudo("update-initramfs -u")
    reboot()


def _install_cuda():
    _unload_nouveau()

    with cd("/mnt"):
        if not exists("/mnt/cuda_7.5.18_linux.run"):
            sudo("wget http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda_7.5.18_linux.run")
        sudo("chmod 755 cuda_7.5.18_linux.run")
        sudo("./cuda_7.5.18_linux.run -silent --driver --toolkit --samples")
    reboot()

    with cd("/usr/local/cuda-7.5/samples/1_Utilities/deviceQuery"):
        sudo("make")


def _install_docker():
    sudo("curl -sSL https://get.docker.com/ | sh")
    sudo("usermod -G docker ubuntu")
    reboot()


def _configure_paths():
    lines = [
        "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH",
        "export PATH=/usr/local/cuda/bin:$PATH".format()
    ]

    append("/home/ubuntu/.bashrc", lines)


def deploy():
    _install_depends()
    _install_docker()
    _install_cuda()
    _configure_paths()

