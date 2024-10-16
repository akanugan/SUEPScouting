import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import os

# Set parameters externally 
from FWCore.ParameterSet.VarParsing import VarParsing
params = VarParsing('analysis')

params.register(
    'isMC', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether the sample is simulation or data'
)

params.register(
    'useWeights', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to use the events weights from a Monte Carlo generator'
)

params.register(
    'filterTrigger', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to ask the event to fire a trigger used in the analysis'
)

params.register(
    'filterMuons', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to ask the event to contain at least two muons'
)

params.register(
    'reducedInfo', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not to store just the reduced information'
)

params.register(
    'trigProcess', 
    'HLT', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)

params.register(
    'GlobalTagData', 
    #'101X_dataRun2_HLT_v7',
    '101X_dataRun2_Prompt_v11', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)

params.register(
    'GlobalTagMC', 
    '102X_upgrade2018_realistic_v15', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'Process name for the HLT paths'
)# check this

params.register(
    'xsec', 
    0.001, 
    VarParsing.multiplicity.singleton,VarParsing.varType.float,
    'Cross-section for a Monte Carlo Sample'
)#fix this

params.register(
    'fileList', 
    'none', 
    VarParsing.multiplicity.singleton,VarParsing.varType.string,
    'input list of files'
)

params.setDefault(
    'maxEvents', 
    -1
)

params.setDefault(
    'outputFile', 
    'test.root' 
)

params.register(
  "era",
  "2018",
  VarParsing.multiplicity.singleton,VarParsing.varType.string,
  "era"
)

params.register(
    'signal', 
    False, 
    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
    'Flag to indicate whether or not signal is run'
)
#params.register(
#    'runScouting', 
#    True, 
#    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
#    'Flag to indicate whether or not signal is run'
#)
#params.register(
#    'runOffline', 
#    False, 
#    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
#    'Flag to indicate whether or not signal is run'
#)

#params.register(
#    'monitor', 
#    False, 
#    VarParsing.multiplicity.singleton,VarParsing.varType.bool,
#    'Flag to indicate whether or not moninor is run'
#)

# Define the process
process = cms.Process("LL")

# Parse command line arguments
params.parseArguments()

# Message Logger settings
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.cerr.FwkReport.reportEvery = 1000 
#process.MessageLogger.cerr.threshold = 'INFO'
#process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#    limit = cms.untracked.int32(-1)
#)

# Set the process options -- Display summary at the end, enable unscheduled execution
process.options = cms.untracked.PSet( 
    allowUnscheduled = cms.untracked.bool(True),
    wantSummary      = cms.untracked.bool(True),
    Rethrow = cms.untracked.vstring("ProductNotFound"), # make this exception fatal
    #Rethrow = cms.untracked.vstring()
    FailPath = cms.untracked.vstring("ProductNotFound")
    #SkipEvent = cms.untracked.vstring('ProductNotFound')
)

# How many events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(params.maxEvents) )

# Input EDM files
#list = FileUtils.loadListFromFile(options.inputFiles)
#readFiles = cms.untracked.vstring(*list)

if params.fileList == "none" : readFiles = params.inputFiles
else : 
    readFiles = cms.untracked.vstring( FileUtils.loadListFromFile (os.environ['CMSSW_BASE']+'/src/PhysicsTools/ScoutingNanoAOD/test/'+params.fileList) )
process.source = cms.Source("PoolSource",
	fileNames = cms.untracked.vstring(readFiles) 
)

# Load the standard set of configuration modules
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')

##--- l1 stage2 digis ---
process.load("EventFilter.L1TRawToDigi.gtStage2Digis_cfi")
process.gtStage2Digis.InputLabel = cms.InputTag( "hltFEDSelectorL1" )
process.load('PhysicsTools.PatAlgos.producersLayer1.patCandidates_cff')

# Load the global tag
from Configuration.AlCa.GlobalTag import GlobalTag
if params.isMC : 
    process.GlobalTag.globaltag = params.GlobalTagMC
else :
    process.GlobalTag.globaltag = params.GlobalTagData

# Define the services needed for the treemaker
process.TFileService = cms.Service("TFileService", 
    fileName = cms.string(params.outputFile)
)

# Tree for the generator weights
process.gentree = cms.EDAnalyzer("LHEWeightsTreeMaker",
    lheInfo = cms.InputTag("externalLHEProducer"),
    genInfo = cms.InputTag("generator"),
    useLHEWeights = cms.bool(params.useWeights)
)

# get rho producer
#runRho = not(params.isMC and params.era=="2016") 
#if(runRho):
#  if params.era=="2015":
#    runRho = False
##if(params.runScouting):
#if(runRho):
#  process.fixedGridRhoFastjetAllScouting = cms.EDProducer("FixedGridRhoProducerFastjetScouting",
#      pfCandidatesTag = cms.InputTag("hltScoutingPFPacker"),
#      electronsTag = cms.InputTag("hltScoutingEgammaPacker"),
#      maxRapidity = cms.double(5.0),
#      gridSpacing = cms.double(0.55),
#  )
#print("RUNNNING TEST| isMC %d| signal %d| data %d| scouting %d| offline %d")



HLTInfo = [
    "DST_DoubleMu1_noVtx_CaloScouting_v*",
    "DST_DoubleMu3_noVtx_CaloScouting_v*",
    "DST_DoubleMu3_noVtx_Mass10_PFScouting_v*",
    "DST_L1HTT_CaloScouting_PFScouting_v*",
    "DST_CaloJet40_CaloScouting_PFScouting_v*",
    "DST_HT250_CaloScouting_v*",
    "DST_HT410_PFScouting_v*",
    "DST_HT450_PFScouting_v*"]
L1Info = [
    # 'L1_HTT200er',
    # 'L1_HTT255er',
    # 'L1_HTT280er',
    # 'L1_HTT320er',
    # 'L1_HTT360er',
    # 'L1_HTT400er',
    # 'L1_HTT450er',
    # 'L1_SingleJet180',
    # 'L1_SingleJet200',
    # 'L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5',
    # 'L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5',
    # 'L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5',
    # 'L1_ETT2000',
    'L1_SingleMuCosmics',
    'L1_SingleMuCosmics_BMTF',
    'L1_SingleMuCosmics_OMTF',
    'L1_SingleMuCosmics_EMTF',
    'L1_SingleMuOpen',
    'L1_SingleMu0_DQ',
    'L1_SingleMu0_BMTF',
    'L1_SingleMu0_OMTF',
    'L1_SingleMu0_EMTF',
    'L1_SingleMu3',
    'L1_SingleMu5',
    'L1_SingleMu7_DQ',
    'L1_SingleMu7',
    'L1_SingleMu12_DQ_BMTF',
    'L1_SingleMu12_DQ_OMTF',
    'L1_SingleMu12_DQ_EMTF',
    'L1_SingleMu15_DQ',
    'L1_SingleMu18',
    'L1_SingleMu20',
    'L1_SingleMu22',
    'L1_SingleMu22_BMTF',
    'L1_SingleMu22_OMTF',
    'L1_SingleMu22_EMTF',
    'L1_SingleMu25',
    'L1_SingleMu6er1p5',
    'L1_SingleMu7er1p5',
    'L1_SingleMu8er1p5',
    'L1_SingleMu9er1p5',
    'L1_SingleMu10er1p5',
    'L1_SingleMu12er1p5',
    'L1_SingleMu14er1p5',
    'L1_SingleMu16er1p5',
    'L1_SingleMu18er1p5',
    'L1_DoubleMu0_OQ',
    'L1_DoubleMu0',
    'L1_DoubleMu0_SQ',
    'L1_DoubleMu0_SQ_OS',
    'L1_DoubleMu0_Mass_Min1',
    'L1_DoubleMu9_SQ',
    'L1_DoubleMu10_SQ',
    'L1_DoubleMu_12_5',
    'L1_DoubleMu_15_5_SQ',
    'L1_DoubleMu_15_7',
    'L1_DoubleMu_15_7_SQ',
    'L1_DoubleMu_15_7_Mass_Min1',
    'L1_DoubleMu18er2p1',
    'L1_DoubleMu0er2p0_SQ_dR_Max1p4',
    'L1_DoubleMu0er2p0_SQ_OS_dR_Max1p4',
    'L1_DoubleMu0er1p5_SQ',
    'L1_DoubleMu0er1p5_SQ_OS',
    'L1_DoubleMu0er1p5_SQ_dR_Max1p4',
    'L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4',
    'L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4',
    'L1_DoubleMu4_SQ_OS',
    'L1_DoubleMu4_SQ_OS_dR_Max1p2',
    'L1_DoubleMu4p5_SQ_OS',
    'L1_DoubleMu4p5_SQ_OS_dR_Max1p2',
    'L1_DoubleMu4p5er2p0_SQ_OS',
    'L1_DoubleMu4p5er2p0_SQ_OS_Mass7to18',
    'L1_TripleMu0_OQ',
    'L1_TripleMu0',
    'L1_TripleMu0_SQ',
    'L1_TripleMu3',
    'L1_TripleMu3_SQ',
    'L1_TripleMu_5SQ_3SQ_0OQ',
    'L1_TripleMu_5_3p5_2p5',
    'L1_TripleMu_5_3_3',
    'L1_TripleMu_5_3_3_SQ',
    'L1_TripleMu_5_5_3',
    'L1_TripleMu_5_3p5_2p5_OQ_DoubleMu_5_2p5_OQ_OS_Mass_5to17',
    'L1_TripleMu_5_3p5_2p5_DoubleMu_5_2p5_OS_Mass_5to17',
    'L1_TripleMu_5_4_2p5_DoubleMu_5_2p5_OS_Mass_5to17',
    'L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9',
    'L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9',
    'L1_QuadMu0_OQ',
    'L1_QuadMu0',
    'L1_QuadMu0_SQ',
    'L1_Mu5_EG23er2p5',
    'L1_Mu7_EG23er2p5',
    'L1_Mu20_EG10er2p5',
    'L1_Mu5_LooseIsoEG20er2p5',
    'L1_Mu7_LooseIsoEG20er2p5',
    'L1_Mu7_LooseIsoEG23er2p5',
    'L1_Mu6_DoubleEG10er2p5',
    'L1_Mu6_DoubleEG12er2p5',
    'L1_Mu6_DoubleEG15er2p5',
    'L1_Mu6_DoubleEG17er2p5',
    'L1_DoubleMu4_SQ_EG9er2p5',
    'L1_DoubleMu5_SQ_EG9er2p5',
    'L1_DoubleMu3_OS_DoubleEG7p5Upsilon',
    'L1_DoubleMu5Upsilon_OS_DoubleEG3',
    'L1_Mu3_Jet30er2p5',
    'L1_Mu3_Jet16er2p5_dR_Max0p4',
    'L1_Mu3_Jet35er2p5_dR_Max0p4',
    'L1_Mu3_Jet60er2p5_dR_Max0p4',
    'L1_Mu3_Jet80er2p5_dR_Max0p4',
    'L1_Mu3_Jet120er2p5_dR_Max0p8',
    'L1_Mu3_Jet120er2p5_dR_Max0p4',
    'L1_Mu3er1p5_Jet100er2p5_ETMHF40',
    'L1_Mu3er1p5_Jet100er2p5_ETMHF50',
    'L1_Mu6_HTT240er',
    'L1_Mu6_HTT250er',
    'L1_Mu10er2p3_Jet32er2p3_dR_Max0p4_DoubleJet32er2p3_dEta_Max1p6',
    'L1_Mu12er2p3_Jet40er2p3_dR_Max0p4_DoubleJet40er2p3_dEta_Max1p6',
    'L1_Mu12er2p3_Jet40er2p1_dR_Max0p4_DoubleJet40er2p1_dEta_Max1p6',
    'L1_DoubleMu0_dR_Max1p6_Jet90er2p5_dR_Max0p8',
    'L1_DoubleMu3_dR_Max1p6_Jet90er2p5_dR_Max0p8',
    'L1_DoubleMu3_SQ_ETMHF50_HTT60er',
    'L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5_OR_DoubleJet40er2p5',
    'L1_DoubleMu3_SQ_ETMHF50_Jet60er2p5',
    'L1_DoubleMu3_SQ_ETMHF60_Jet60er2p5',
    'L1_DoubleMu3_SQ_HTT220er',
    'L1_DoubleMu3_SQ_HTT240er',
    'L1_DoubleMu3_SQ_HTT260er',
    'L1_SingleEG8er2p5',
    'L1_SingleEG10er2p5',
    'L1_SingleEG15er2p5',
    'L1_SingleEG26er2p5',
    'L1_SingleEG34er2p5',
    'L1_SingleEG36er2p5',
    'L1_SingleEG38er2p5',
    'L1_SingleEG40er2p5',
    'L1_SingleEG42er2p5',
    'L1_SingleEG45er2p5',
    'L1_SingleEG50',
    'L1_SingleEG60',
    'L1_SingleLooseIsoEG28er1p5',
    'L1_SingleLooseIsoEG30er1p5',
    'L1_SingleIsoEG24er2p1',
    'L1_SingleIsoEG24er1p5',
    'L1_SingleIsoEG26er2p5',
    'L1_SingleIsoEG26er2p1',
    'L1_SingleIsoEG26er1p5',
    'L1_SingleIsoEG28er2p5',
    'L1_SingleIsoEG28er2p1',
    'L1_SingleIsoEG28er1p5',
    'L1_SingleIsoEG30er2p5',
    'L1_SingleIsoEG30er2p1',
    'L1_SingleIsoEG32er2p5',
    'L1_SingleIsoEG32er2p1',
    'L1_SingleIsoEG34er2p5',
    'L1_IsoEG32er2p5_Mt40',
    'L1_IsoEG32er2p5_Mt44',
    'L1_IsoEG32er2p5_Mt48',
    'L1_DoubleEG_15_10_er2p5',
    'L1_DoubleEG_20_10_er2p5',
    'L1_DoubleEG_22_10_er2p5',
    'L1_DoubleEG_25_12_er2p5',
    'L1_DoubleEG_25_14_er2p5',
    'L1_DoubleEG_27_14_er2p5',
    'L1_DoubleEG_LooseIso20_10_er2p5',
    'L1_DoubleEG_LooseIso22_10_er2p5',
    'L1_DoubleEG_LooseIso22_12_er2p5',
    'L1_DoubleEG_LooseIso25_12_er2p5',
    'L1_DoubleLooseIsoEG22er2p1',
    'L1_DoubleLooseIsoEG24er2p1',
    'L1_TripleEG_16_12_8_er2p5',
    'L1_TripleEG_16_15_8_er2p5',
    'L1_TripleEG_18_17_8_er2p5',
    'L1_TripleEG_18_18_12_er2p5',
    'L1_TripleEG16er2p5',
    'L1_LooseIsoEG26er2p1_Jet34er2p5_dR_Min0p3',
    'L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3',
    'L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3',
    'L1_LooseIsoEG24er2p1_HTT100er',
    'L1_LooseIsoEG26er2p1_HTT100er',
    'L1_LooseIsoEG28er2p1_HTT100er',
    'L1_LooseIsoEG30er2p1_HTT100er',
    'L1_DoubleEG8er2p5_HTT260er',
    'L1_DoubleEG8er2p5_HTT280er',
    'L1_DoubleEG8er2p5_HTT300er',
    'L1_DoubleEG8er2p5_HTT320er',
    'L1_DoubleEG8er2p5_HTT340er',
    'L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3',
    'L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3',
    'L1_LooseIsoEG22er2p1_Tau70er2p1_dR_Min0p3',
    'L1_SingleTau120er2p1',
    'L1_SingleTau130er2p1',
    'L1_DoubleTau70er2p1',
    'L1_DoubleIsoTau32er2p1',
    'L1_DoubleIsoTau34er2p1',
    'L1_DoubleIsoTau36er2p1',
    'L1_Mu18er2p1_Tau24er2p1',
    'L1_Mu18er2p1_Tau26er2p1',
    'L1_Mu22er2p1_IsoTau32er2p1',
    'L1_Mu22er2p1_IsoTau34er2p1',
    'L1_Mu22er2p1_IsoTau36er2p1',
    'L1_Mu22er2p1_IsoTau40er2p1',
    'L1_Mu22er2p1_Tau70er2p1',
    'L1_IsoTau40er2p1_ETMHF90',
    'L1_IsoTau40er2p1_ETMHF100',
    'L1_IsoTau40er2p1_ETMHF110',
    'L1_IsoTau40er2p1_ETMHF120',
    'L1_QuadJet36er2p5_IsoTau52er2p1',
    'L1_SingleJet35',
    'L1_SingleJet60',
    'L1_SingleJet90',
    'L1_SingleJet120',
    'L1_SingleJet180',
    'L1_SingleJet200',
    'L1_SingleJet35er2p5',
    'L1_SingleJet60er2p5',
    'L1_SingleJet90er2p5',
    'L1_SingleJet120er2p5',
    'L1_SingleJet140er2p5',
    'L1_SingleJet160er2p5',
    'L1_SingleJet180er2p5',
    'L1_SingleJet35_FWD3p0',
    'L1_SingleJet60_FWD3p0',
    'L1_SingleJet90_FWD3p0',
    'L1_SingleJet120_FWD3p0',
    'L1_SingleJet8erHE',
    'L1_SingleJet10erHE',
    'L1_SingleJet12erHE',
    'L1_SingleJet140er2p5_ETMHF80',
    'L1_SingleJet140er2p5_ETMHF90',
    'L1_DoubleJet40er2p5',
    'L1_DoubleJet100er2p5',
    'L1_DoubleJet120er2p5',
    'L1_DoubleJet150er2p5',
    'L1_DoubleJet100er2p3_dEta_Max1p6',
    'L1_DoubleJet112er2p3_dEta_Max1p6',
    'L1_DoubleJet30er2p5_Mass_Min150_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min200_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min250_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min300_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min330_dEta_Max1p5',
    'L1_DoubleJet30er2p5_Mass_Min360_dEta_Max1p5',
    'L1_DoubleJet_90_30_DoubleJet30_Mass_Min620',
    'L1_DoubleJet_100_30_DoubleJet30_Mass_Min620',
    'L1_DoubleJet_110_35_DoubleJet35_Mass_Min620',
    'L1_DoubleJet_115_40_DoubleJet40_Mass_Min620',
    'L1_DoubleJet_120_45_DoubleJet45_Mass_Min620',
    'L1_DoubleJet_115_40_DoubleJet40_Mass_Min620_Jet60TT28',
    'L1_DoubleJet_120_45_DoubleJet45_Mass_Min620_Jet60TT28',
    'L1_DoubleJet35_Mass_Min450_IsoTau45_RmOvlp',
    'L1_DoubleJet_80_30_Mass_Min420_IsoTau40_RmOvlp',
    'L1_DoubleJet_80_30_Mass_Min420_Mu8',
    'L1_DoubleJet_80_30_Mass_Min420_DoubleMu0_SQ',
    'L1_TripleJet_95_75_65_DoubleJet_75_65_er2p5',
    'L1_TripleJet_100_80_70_DoubleJet_80_70_er2p5',
    'L1_TripleJet_105_85_75_DoubleJet_85_75_er2p5',
    'L1_QuadJet_95_75_65_20_DoubleJet_75_65_er2p5_Jet20_FWD3p0',
    'L1_QuadJet60er2p5',
    'L1_HTT280er_QuadJet_70_55_40_35_er2p4',
    'L1_HTT320er_QuadJet_70_55_40_40_er2p4',
    'L1_HTT320er_QuadJet_80_60_er2p1_45_40_er2p3',
    'L1_HTT320er_QuadJet_80_60_er2p1_50_45_er2p3',
    'L1_HTT120er',
    'L1_HTT160er',
    'L1_HTT200er',
    'L1_HTT255er',
    'L1_HTT280er',
    'L1_HTT320er',
    'L1_HTT360er',
    'L1_HTT400er',
    'L1_HTT450er',
    'L1_ETT1200',
    'L1_ETT1600',
    'L1_ETT2000',
    'L1_ETM120',
    'L1_ETM150',
    'L1_ETMHF100',
    'L1_ETMHF110',
    'L1_ETMHF120',
    'L1_ETMHF130',
    'L1_ETMHF140',
    'L1_ETMHF150',
    'L1_ETMHF90_HTT60er',
    'L1_ETMHF100_HTT60er',
    'L1_ETMHF110_HTT60er',
    'L1_ETMHF120_HTT60er',
    'L1_ETMHF130_HTT60er',
    'L1_ETMHF120_NotSecondBunchInTrain',
    'L1_ETMHF110_HTT60er_NotSecondBunchInTrain',
    'L1_SingleMuOpen_NotBptxOR',
    'L1_SingleMuOpen_er1p4_NotBptxOR_3BX',
    'L1_SingleMuOpen_er1p1_NotBptxOR_3BX',
    'L1_SingleJet20er2p5_NotBptxOR',
    'L1_SingleJet20er2p5_NotBptxOR_3BX',
    'L1_SingleJet43er2p5_NotBptxOR_3BX',
    'L1_SingleJet46er2p5_NotBptxOR_3BX',
    'L1_AlwaysTrue',
    'L1_ZeroBias',
    'L1_ZeroBias_copy',
    'L1_MinimumBiasHF0_AND_BptxAND',
    'L1_NotBptxOR',
    'L1_BptxOR',
    'L1_BptxXOR',
    'L1_BptxPlus',
    'L1_BptxMinus',
    'L1_UnpairedBunchBptxPlus',
    'L1_UnpairedBunchBptxMinus',
    'L1_IsolatedBunch',
    'L1_FirstBunchBeforeTrain',
    'L1_FirstBunchInTrain',
    'L1_SecondBunchInTrain',
    'L1_SecondLastBunchInTrain',
    'L1_LastBunchInTrain',
    'L1_FirstBunchAfterTrain',
    'L1_LastCollisionInTrain',
    'L1_FirstCollisionInTrain',
    'L1_FirstCollisionInOrbit',
    'L1_BPTX_NotOR_VME',
    'L1_BPTX_OR_Ref3_VME',
    'L1_BPTX_OR_Ref4_VME',
    'L1_BPTX_RefAND_VME',
    'L1_BPTX_AND_Ref1_VME',
    'L1_BPTX_AND_Ref3_VME',
    'L1_BPTX_AND_Ref4_VME',
    'L1_BPTX_BeamGas_Ref1_VME',
    'L1_BPTX_BeamGas_Ref2_VME',
    'L1_BPTX_BeamGas_B1_VME',
    'L1_BPTX_BeamGas_B2_VME',
    'L1_CDC_SingleMu_3_er1p2_TOP120_DPHI2p618_3p142',
    'L1_HCAL_LaserMon_Trig',
    'L1_HCAL_LaserMon_Veto',
    'L1_TOTEM_1',
    'L1_TOTEM_2',
    'L1_TOTEM_3',
    'L1_TOTEM_4',
]
runSig = False
#if "SUEP" in readFiles[0]:
#  runSig = True
#if params.signal:
#  runSig = True

process.mmtree = cms.EDAnalyzer('ScoutingNanoAOD',
    doL1              = cms.bool(True),
    doData            = cms.bool(not params.isMC and not params.signal),
    doSignal          = cms.bool(runSig), 
    isMC              = cms.bool(params.isMC),
    #monitor           = cms.bool(params.monitor),
    era_16            = cms.bool(params.era == "2016"),
    #runScouting          = cms.bool(params.runScouting),
    #runOffline          = cms.bool(params.runOffline),
    #runScouting          = cms.bool(not(params.isMC and params.era == 2016)), #always run scouting except 2016MC
    #runOffline          = cms.bool(params.isMC and not params.signal), #only run offline for QCD
    stageL1Trigger    = cms.uint32(2),

    hltProcess=cms.string("HLT"),
    bits              = cms.InputTag("TriggerResults", "", "HLT"),
    
    triggerresults   = cms.InputTag("TriggerResults", "", params.trigProcess),
    triggerConfiguration = cms.PSet(
    	hltResults               = cms.InputTag('TriggerResults','','HLT'),
    	#l1tResults               = cms.InputTag(''),
    	daqPartitions            = cms.uint32(1),
    	l1tIgnoreMaskAndPrescale = cms.bool(False),
    	throw                    = cms.bool(False)
  	),
    ReadPrescalesFromFile = cms.bool( False ),
    AlgInputTag = cms.InputTag("gtStage2Digis"),
    l1tAlgBlkInputTag = cms.InputTag("gtStage2Digis"),
    l1tExtBlkInputTag = cms.InputTag("gtStage2Digis"),
    l1Seeds           = cms.vstring(L1Info),
    hltSeeds          = cms.vstring(HLTInfo),
    muons             = cms.InputTag("hltScoutingMuonPacker"),
    electrons         = cms.InputTag("hltScoutingEgammaPacker"),
    photons           = cms.InputTag("hltScoutingEgammaPacker"),
    pfcands           = cms.InputTag("hltScoutingPFPacker"),
    pfjetsoff         = cms.InputTag("ak4PFJets"),
    pfjets            = cms.InputTag("hltScoutingPFPacker"),
    vertices_2016     = cms.InputTag("hltScoutingPFPacker",""), #Will try 2016 Packer and default to others if failed
    vertices          = cms.InputTag("hltScoutingPrimaryVertexPacker","primaryVtx"),
    offlineTracks     = cms.InputTag("particleFlow"),
    offlineTracks2     = cms.InputTag("packedPFCandidates"),
    #offlineTracks     = cms.InputTag("generalTracks"),
    pileupinfo        = cms.InputTag("addPileupInfo"),
    pileupinfo_sig    = cms.InputTag("slimmedAddPileupInfo"),
    geneventinfo     = cms.InputTag("generator"),
    gens              = cms.InputTag("genParticles"),
    gens_sig          = cms.InputTag("genParticles"),
    #gens_sig          = cms.InputTag("prunedGenParticles"),
    #rho               = cms.InputTag("fixedGridRhoFastjetAllScouting"),
    rho2              = cms.InputTag("hltScoutingPFPacker","rho"),
#    genLumi            = cms.InputTag("generator"),

    # for JEC corrections eventually
    #L1corrAK4_DATA    = cms.FileInPath('CMSDIJET/DijetScoutingRootTreeMaker/data/80X_dataRun2_HLT_v12/80X_dataRun2_HLT_v12_L1FastJet_AK4CaloHLT.txt'),
    #L2corrAK4_DATA    = cms.FileInPath('CMSDIJET/DijetScoutingRootTreeMaker/data/80X_dataRun2_HLT_v12/80X_dataRun2_HLT_v12_L2Relative_AK4CaloHLT.txt'),
    #L3corrAK4_DATA    = cms.FileInPath('CMSDIJET/DijetScoutingRootTreeMaker/data/80X_dataRun2_HLT_v12/80X_dataRun2_HLT_v12_L3Absolute_AK4CaloHLT.txt'),
)
#process.Tracer = cms.Service("Tracer")

# add any intermediate modules to this task list
# then unscheduled mode will call them automatically when the final module (mmtree) consumes their products
#if(params.runScouting):
#if(runRho):
#  process.myTask = cms.Task(process.fixedGridRhoFastjetAllScouting)

if(params.isMC):
#if(runSig or (params.isMC and not params.era=="2016")):
#if(runSig):
#if(params.signal):
  #print("test1",runSig,params.isMC,params.era,(params.isMC and not params.era=="2016"))
  from PhysicsTools.PatUtils.l1PrefiringWeightProducer_cfi import l1PrefiringWeightProducer
  process.prefiringweight = l1PrefiringWeightProducer.clone(
  ThePhotons           = cms.InputTag("hltScoutingEgammaPacker"),
  TheMuons             = cms.InputTag("hltScoutingMuonPacker"),
  TheJets            = cms.InputTag("hltScoutingPFPacker"),
  #TheJets = cms.InputTag("slimmedJets"), #this should be the slimmedJets collection with up to date JECs 
  #TheJets = cms.InputTag("updatedPatJetsUpdatedJEC"), #this should be the slimmedJets collection with up to date JECs 
  DataEraECAL = cms.string("2017BtoF"), #Use 2016BtoH for 2016
  DataEraMuon = cms.string("20172018"), #Use 2016 for 2016
  UseJetEMPt = cms.bool(False),
  PrefiringRateSystematicUnctyECAL = cms.double(0.2),
  PrefiringRateSystematicUnctyMuon = cms.double(0.2)
  )
  process.p = cms.Path(process.prefiringweight* process.mmtree)
else:
  # process.p = cms.Path(process.mmtree)
  process.p = cms.Path(process.gtStage2Digis + process.mmtree)
#if(params.runScouting):
#if(runRho):
#  process.p.associate(process.myTask)
