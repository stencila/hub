from ec2 import EC2
from virtualbox import VirtualBox

providers = {
    'ec2': EC2(),
    'vbox': VirtualBox(),
}
