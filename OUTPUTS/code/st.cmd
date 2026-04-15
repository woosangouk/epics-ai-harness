#!../../bin/linux-x86_64/phytronIOC

< envPaths

cd "${TOP}"

dbLoadDatabase "dbd/phytronIOC.dbd"
phytronIOC_registerRecordDeviceDriver pdbbase

epicsEnvSet("P", "PHYTRON:")
epicsEnvSet("R", "M1:")
epicsEnvSet("PORT", "MCC1")
epicsEnvSet("HOST", "192.168.10.53")
epicsEnvSet("TCP_PORT", "22222")

drvAsynIPPortConfigure("$(PORT)", "$(HOST):$(TCP_PORT)", 0, 0, 0)

asynSetTraceMask("$(PORT)", 0, 0x9)
asynSetTraceIOMask("$(PORT)", 0, 0x2)

dbLoadRecords("db/phytron.db", "P=$(P),R=$(R),PORT=$(PORT)")

cd "${TOP}/iocBoot/${IOC}"
iocInit