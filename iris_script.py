import glob
import os
import iris
from sqlalchemy import create_engine
from iris import ipm

# switch namespace to the %SYS namespace
iris.system.Process.SetNamespace("%SYS")

# set credentials to not expire
iris.cls('Security.Users').UnExpireUserPasswords("*")

# switch namespace to IRISAPP built by merge.cpf
iris.system.Process.SetNamespace("USER")

# load ipm package listed in module.xml
#iris.cls('%ZPM.PackageManager').Shell("load /home/irisowner/dev -v")
assert ipm('load /home/irisowner/dev -v')