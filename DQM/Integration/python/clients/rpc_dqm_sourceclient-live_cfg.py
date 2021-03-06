from __future__ import print_function

import FWCore.ParameterSet.Config as cms

## Use RECO Muons flag
useMuons = False
isOfflineDQM = False

process = cms.Process("RPCDQM")

############## Event Source #####################
# for live online DQM in P5
process.load("DQM.Integration.config.inputsource_cfi")

# for testing in lxplus
#process.load("DQM.Integration.config.fileinputsource_cfi")

############### HLT Filter#######################
# 0=random, 1=physics, 2=calibration, 3=technical
process.hltTriggerTypeFilter = cms.EDFilter("HLTTriggerTypeFilter",
    SelectedTriggerType = cms.int32(1)
)

################# Geometry  #####################
#process.load("Geometry.MuonCommonData.muonIdealGeometryXML_cfi")
#process.load("Geometry.RPCGeometry.rpcGeometry_cfi")
#process.load("Geometry.MuonNumbering.muonNumberingInitialization_cfi")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
################ Condition ######################
# Condition for P5 cluster
process.load("DQM.Integration.config.FrontierCondition_GT_cfi")
# Condition for lxplus: change and possibly customise the GT
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#from Configuration.AlCa.GlobalTag import GlobalTag as gtCustomise
#process.GlobalTag = gtCustomise(process.GlobalTag, 'auto:run2_data', '')
#process.GlobalTag.globaltag = "102X_dataRun2_Express_v4"
process.GlobalTag.RefreshEachRun = cms.untracked.bool(True)

############# DQM Cetral Modules ################
#process.load("DQMServices.Core.DQM_cfg")

############## DQM Enviroment ###################
process.load("DQM.Integration.config.environment_cfi")
process.dqmEnv.subSystemFolder = 'RPC'
process.dqmSaver.tag = 'RPC'

process.DQMStore.referenceFileName = '/dqmdata/dqm/reference/rpc_reference.root'

############### Scaler Producer #################
process.load("EventFilter.ScalersRawToDigi.ScalersRawToDigi_cfi")

############## RPC Unpacker  ####################
process.rpcunpacker = cms.EDProducer("RPCUnpackingModule",
    InputLabel = cms.InputTag("source"),
    doSynchro = cms.bool(False)
)

### RPC RawToDigi - from TwinMux
process.load("EventFilter.RPCRawToDigi.RPCTwinMuxRawToDigi_cff")

### RPC RawToDigi - from CPPF
process.load("EventFilter.RPCRawToDigi.RPCCPPFRawToDigi_cff")
# process.load("EventFilter.RPCRawToDigi.RPCCPPFRawToDigi_sqlite_cff") #to load CPPF link maps from the local DB

### RPC RawToDigi - from OMTF
process.omtfStage2Digis = cms.EDProducer("OmtfUnpacker",
  inputLabel = cms.InputTag('rawDataCollector'),
)

process.load("EventFilter.RPCRawToDigi.RPCDigiMerger_cff")
process.rpcDigiMerger.inputTagTwinMuxDigis = 'rpcTwinMuxRawToDigi'
process.rpcDigiMerger.inputTagOMTFDigis = 'omtfStage2Digis'
process.rpcDigiMerger.inputTagCPPFDigis = 'rpcCPPFRawToDigi'

################# RPC Rec Hits  #################
process.load("RecoLocalMuon.RPCRecHit.rpcRecHits_cfi")
process.rpcRecHits.rpcDigiLabel = 'rpcunpacker'
#######################################################
### RPCRecHit - from Merger
process.rpcMergerRecHits = process.rpcRecHits.clone()
process.rpcMergerRecHits.rpcDigiLabel = cms.InputTag('rpcDigiMerger')

################ DQM Digi Module ################
### DQM - from legacy
process.load("DQM.RPCMonitorDigi.RPCDigiMonitoring_cfi")
process.rpcdigidqm.UseMuon =  useMuons
process.rpcdigidqm.NoiseFolder = cms.untracked.string("AllHits")
process.rpcdigidqm.RecHitLabel = cms.InputTag("rpcRecHits")
### DQM - from Merger
process.rpcMergerdigidqm = process.rpcdigidqm.clone()
process.rpcMergerdigidqm.NoiseFolder = cms.untracked.string("AllHitsMerger")
process.rpcMergerdigidqm.RecHitLabel = cms.InputTag("rpcMergerRecHits")

#######################################################

################# DCS Info ######################
process.load("DQM.RPCMonitorDigi.RPCDcsInfo_cfi")

################# DQM Client Modules ############
process.load("DQM.RPCMonitorClient.RPCDqmClient_cfi")
process.rpcdqmclient.RPCDqmClientList = cms.untracked.vstring("RPCMultiplicityTest", "RPCDeadChannelTest", "RPCClusterSizeTest", "RPCOccupancyTest","RPCNoisyStripTest")
process.rpcdqmclient.DiagnosticPrescale = cms.untracked.int32(1)
process.rpcdqmclient.MinimumRPCEvents  = cms.untracked.int32(100)
process.rpcdqmclient.OfflineDQM = cms.untracked.bool(isOfflineDQM)
process.rpcdqmclient.RecHitTypeFolder = cms.untracked.string("AllHits")
### Merger
process.rpcMergerdqmclient = process.rpcdqmclient.clone()
process.rpcMergerdqmclient.RecHitTypeFolder = cms.untracked.string("AllHitsMerger")
################# Other Clients #################
#process.load("DQM.RPCMonitorClient.RPCMon_SS_Dbx_Global_cfi")

################### FED #########################
process.load("DQM.RPCMonitorClient.RPCMonitorRaw_cfi")
process.load("DQM.RPCMonitorClient.RPCFEDIntegrity_cfi")
process.load("DQM.RPCMonitorClient.RPCMonitorLinkSynchro_cfi")

########### RPC Event Summary Module ############
process.load("DQM.RPCMonitorClient.RPCEventSummary_cfi")
process.rpcEventSummary.OfflineDQM = cms.untracked.bool(isOfflineDQM )
process.rpcEventSummary.MinimumRPCEvents  = cms.untracked.int32(10000)
process.rpcEventSummary.RecHitTypeFolder = cms.untracked.string("AllHits")
### Merger
process.rpcEventSummaryMerger = process.rpcEventSummary.clone()
process.rpcEventSummaryMerger.RecHitTypeFolder = cms.untracked.string("AllHitsMerger")

################# Quality Tests #################
from DQMServices.Core.DQMQualityTester import DQMQualityTester
process.qTesterRPC = DQMQualityTester(
    qtList = cms.untracked.FileInPath('DQM/RPCMonitorClient/test/RPCQualityTests.xml'),
    prescaleFactor = cms.untracked.int32(5),
    qtestOnEndLumi = cms.untracked.bool(True),
    qtestOnEndRun = cms.untracked.bool(True)
)

############## Chamber Quality ##################
process.load("DQM.RPCMonitorClient.RPCChamberQuality_cfi")
process.rpcChamberQuality.OfflineDQM = cms.untracked.bool(isOfflineDQM )
process.rpcChamberQuality.RecHitTypeFolder = cms.untracked.string("AllHits")
process.rpcChamberQuality.MinimumRPCEvents  = cms.untracked.int32(10000)
### Merger
process.rpcChamberQualityMerger = process.rpcChamberQuality.clone()
process.rpcChamberQualityMerger.RecHitTypeFolder = cms.untracked.string("AllHitsMerger")

###############  Sequences ######################
process.rpcSource = cms.Sequence( process.rpcunpacker
                      * (process.rpcTwinMuxRawToDigi + process.rpcCPPFRawToDigi + process.omtfStage2Digis) 
                      * process.rpcDigiMerger 
                      * (process.rpcRecHits + process.rpcMergerRecHits)
                      * process.scalersRawToDigi
                      * (process.rpcdigidqm + process.rpcMergerdigidqm)
                      * process.rpcMonitorRaw*process.rpcDcsInfo*process.qTesterRPC
                    )
process.rpcClient = cms.Sequence(process.rpcdqmclient*process.rpcMergerdqmclient*process.rpcChamberQuality*process.rpcChamberQualityMerger*process.rpcEventSummary*process.rpcEventSummaryMerger*process.dqmEnv*process.dqmSaver)
process.p = cms.Path(process.hltTriggerTypeFilter*process.rpcSource*process.rpcClient)

process.rpcunpacker.InputLabel = cms.InputTag("rawDataCollector")
process.scalersRawToDigi.scalersInputTag = cms.InputTag("rawDataCollector")
process.rpcCPPFRawToDigi.inputTag = cms.InputTag("rawDataCollector")
#--------------------------------------------------
# Heavy Ion Specific Fed Raw Data Collection Label
#--------------------------------------------------

print("Running with run type = ", process.runType.getRunType())

if (process.runType.getRunType() == process.runType.hi_run):
    process.rpcunpacker.InputLabel = cms.InputTag("rawDataRepacker")
    process.scalersRawToDigi.scalersInputTag = cms.InputTag("rawDataRepacker")
    process.rpcTwinMuxRawToDigi.inputTag = cms.InputTag("rawDataRepacker")
    process.rpcCPPFRawToDigi.inputTag = cms.InputTag("rawDataRepacker")
    process.omtfStage2Digis.inputLabel = cms.InputTag("rawDataRepacker")
    process.rpcEventSummary.MinimumRPCEvents  = cms.untracked.int32(100000)
    process.rpcEventSummaryMerger.MinimumRPCEvents  = cms.untracked.int32(100000)

### process customizations included here
from DQM.Integration.config.online_customizations_cfi import *
process = customise(process)
