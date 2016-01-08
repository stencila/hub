from ec2 import EC2
from localhost import Localhost
from virtualbox import VirtualBox

providers = {
    'ec2': EC2(),
    'local': Localhost(),
    'vbox': VirtualBox(),
}
