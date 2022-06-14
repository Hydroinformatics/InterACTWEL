#Generated using GenerateMakefile by Zhiqiang Yu, hawklorry@gmail.com
#Thursday, June 11, 2020 8:34:02 PM

#Define compiler
CC=/usr/bin/gcc-9
FC=/usr/bin/gfortran-9

#C Flag, remove -Wall if don't want all the warning information
CFLAG=-c -Wall -fmessage-length=0
#Fortran Flag, remove -Wall if don't want all the warning information
#FFLAG=-c -Wall -ffree-line-length-none -fmessage-length=0 -funderscoring -fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow
FFLAG=-c -Wall -ffree-line-length-none -fmessage-length=0 -fcheck=all -fbacktrace -ffpe-trap=invalid,zero,overflow -fno-underscoring -march=native -O3 -DNDEBUG -O3 -funroll-loops -finline-functions -flto
#Dedug Flag
DFLAG=-O0 -g -fbounds-check -Wextra
#Release Flag
RFLAG=-O3
#Flag for long fix fortran codes, used for some special fortran files
LONGFIX=-ffixed-line-length-0
#Flag for long free fortran codes, used for some special fortran files
LONGFREE=-ffree-line-length-none
#Flag for target machine architecture.
#Note: MinGW doesn't support 64-bit architecture. Replace -m64 with empty string instead.
ARCH32=-m32
ARCH64=


OBJECTS_REL64=  rel64/addh.o rel64/albedo.o rel64/allocate_parms.o rel64/allocatewr.o rel64/alph.o rel64/anfert.o rel64/apex_day.o rel64/apply.o rel64/ascrv.o rel64/atri.o rel64/aunif.o rel64/autoirr.o rel64/aveval.o rel64/bacteria.o rel64/biofilm.o rel64/biozone.o rel64/bmpfixed.o rel64/bmpinit.o rel64/bmp_det_pond.o rel64/bmp_ri_pond.o rel64/bmp_sand_filter.o rel64/bmp_sed_pond.o rel64/bmp_wet_pond.o rel64/buffer.o rel64/burnop.o rel64/canopyint.o rel64/caps.o rel64/carbon_new.o rel64/carbon_zhang2.o rel64/cfactor.o rel64/check_wr.o rel64/chkcst.o rel64/clgen.o rel64/clicon.o rel64/command.o rel64/conapply.o rel64/confert.o rel64/crackflow.o rel64/crackvol.o rel64/curno.o rel64/dailycn.o rel64/decay.o rel64/depstor.o rel64/distrib_bmps.o rel64/dormant.o rel64/drains.o rel64/dstn1.o rel64/ee.o rel64/eiusle.o rel64/enrsb.o rel64/erfc.o rel64/estimate_ksat.o rel64/etact.o rel64/etpot.o rel64/expo.o rel64/fert.o rel64/filter.o rel64/filtw.o rel64/finalbal.o rel64/gcycl.o rel64/getallo.o rel64/grass_wway.o rel64/graze.o rel64/grow.o rel64/gwmod.o rel64/gwmod_deep.o rel64/gwnutr.o rel64/gw_no3.o rel64/h2omgt_init.o rel64/harvestop.o rel64/harvgrainop.o rel64/harvkillop.o rel64/header.o rel64/headout.o rel64/hhnoqual.o rel64/hhwatqual.o rel64/hmeas.o rel64/hqdav.o rel64/hruaa.o rel64/hruallo.o rel64/hruday.o rel64/hrumon.o rel64/hrupond.o rel64/hrupondhr.o rel64/hruyr.o rel64/hydroinit.o rel64/icl.o rel64/impndaa.o rel64/impndday.o rel64/impndmon.o rel64/impndyr.o rel64/impnd_init.o rel64/irrigate.o rel64/irrsub.o rel64/irr_rch.o rel64/irr_res.o rel64/jdt.o rel64/killop.o rel64/lakeq.o rel64/latsed.o rel64/layersplit.o rel64/lidinit.o rel64/lids.o rel64/lid_cistern.o rel64/lid_greenroof.o rel64/lid_porpavement.o rel64/lid_raingarden.o rel64/log_normal.o rel64/lwqdef.o rel64/main.o rel64/ncsed_leach.o rel64/ndenit.o rel64/newtillmix.o rel64/nfix.o rel64/nitvol.o rel64/nlch.o rel64/nminrl.o rel64/noqual.o rel64/npup.o rel64/nrain.o rel64/nup.o rel64/nuts.o rel64/openwth.o rel64/operatn.o rel64/orgn.o rel64/orgncswat.o rel64/origtile.o rel64/ovr_sed.o rel64/percmacro.o rel64/percmain.o rel64/percmicro.o rel64/pestlch.o rel64/pestw.o rel64/pesty.o rel64/pgen.o rel64/pgenhr.o rel64/pkq.o rel64/plantmod.o rel64/plantop.o rel64/pmeas.o rel64/pminrl.o rel64/pminrl2.o rel64/pond.o rel64/pondhr.o rel64/pothole.o rel64/potholehr.o rel64/print_hyd.o rel64/psed.o rel64/qman.o rel64/ran1.o rel64/rchaa.o rel64/rchday.o rel64/rchinit.o rel64/rchmon.o rel64/rchuse.o rel64/rchyr.o rel64/reachout.o rel64/readatmodep.o rel64/readbsn.o rel64/readchm.o rel64/readcnst.o rel64/readfcst.o rel64/readfert.o rel64/readfig.o rel64/readfile.o rel64/readgw.o rel64/readhru.o rel64/readinpt.o rel64/readlup.o rel64/readlwq.o rel64/readmgt.o rel64/readmon.o rel64/readops.o rel64/readpest.o rel64/readplant.o rel64/readpnd.o rel64/readres.o rel64/readrte.o rel64/readru.o rel64/readsdr.o rel64/readsepticbz.o rel64/readseptwq.o rel64/readsno.o rel64/readsol.o rel64/readsub.o rel64/readswq.o rel64/readtill.o rel64/readwr.o rel64/readhruwr.o rel64/readstrwr.o rel64/readurban.o rel64/readwgn.o rel64/readwus.o rel64/readwwq.o rel64/readyr.o rel64/reccnst.o rel64/recday.o rel64/rechour.o rel64/recmon.o rel64/recyear.o rel64/regres.o rel64/res.o rel64/resbact.o rel64/resetlu.o rel64/reshr.o rel64/resinit.o rel64/resnut.o rel64/rewind_init.o rel64/rhgen.o rel64/rootfr.o rel64/route.o rel64/routels.o rel64/routeunit.o rel64/routres.o rel64/rsedaa.o rel64/rseday.o rel64/rsedmon.o rel64/rsedyr.o rel64/rtbact.o rel64/rtday.o rel64/rteinit.o rel64/rthmusk.o rel64/rthpest.o rel64/rthsed.o rel64/rthvsc.o rel64/rtmusk.o rel64/rtout.o rel64/rtpest.o rel64/rtsed.o rel64/rtsed_bagnold.o rel64/rtsed_kodatie.o rel64/rtsed_molinas_wu.o rel64/rtsed_yangsand.o rel64/sat_excess.o rel64/save.o rel64/saveconc.o rel64/schedule_ops.o rel64/sched_mgt.o rel64/set_wrprior.o rel64/simulate.o rel64/sim_initday.o rel64/sim_inityr.o rel64/slrgen.o rel64/smeas.o rel64/snom.o rel64/soil_chem.o rel64/soil_par.o rel64/soil_phys.o rel64/soil_write.o rel64/solp.o rel64/solt.o rel64/std1.o rel64/std2.o rel64/std3.o rel64/stdaa.o rel64/storeinitial.o rel64/structure.o rel64/subaa.o rel64/subbasin.o rel64/subday.o rel64/submon.o rel64/substor.o rel64/subwq.o rel64/subyr.o rel64/sub_subbasin.o rel64/sumhyd.o rel64/sumv.o rel64/surface.o rel64/surfstor.o rel64/surfst_h2o.o rel64/surq_daycn.o rel64/surq_greenampt.o rel64/swbl.o rel64/sweep.o rel64/swu.o rel64/sw_init.o rel64/tair.o rel64/tgen.o rel64/theta.o rel64/tillfactor.o rel64/tillmix.o rel64/tmeas.o rel64/tran.o rel64/transfer.o rel64/tstr.o rel64/ttcoef.o rel64/ttcoef_wway.o rel64/urban.o rel64/urbanhr.o rel64/urb_bmp.o rel64/varinit.o rel64/vbl.o rel64/virtual.o rel64/volq.o rel64/washp.o rel64/watbal.o rel64/water_hru.o rel64/watqual.o rel64/watqual2.o rel64/wattable.o rel64/watuse.o rel64/weatgn.o rel64/wetlan.o rel64/wmeas.o rel64/wndgen.o rel64/writea.o rel64/writeaa.o rel64/writed.o rel64/writem.o rel64/xmon.o rel64/ysed.o rel64/zero0.o rel64/zero1.o rel64/zero2.o rel64/zeroini.o rel64/zero_urbn.o

NAMEREL64=swat_rel64
rel64:rel64_mkdir ${NAMEREL64}

rel64_mkdir:
	mkdir -p rel64

${NAMEREL64}: ${OBJECTS_REL64}
	${FC} ${OBJECTS_REL64} ${ARCH64} -static -o ${NAMEREL64}


rel64/addh.o: addh.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  addh.f -o rel64/addh.o -I rel64

rel64/albedo.o: albedo.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  albedo.f -o rel64/albedo.o -I rel64

rel64/allocate_parms.o: allocate_parms.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  allocate_parms.f -o rel64/allocate_parms.o -I rel64

rel64/allocatewr.o: allocatewr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  allocatewr.f -o rel64/allocatewr.o -I rel64

rel64/alph.o: alph.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  alph.f -o rel64/alph.o -I rel64

rel64/anfert.o: anfert.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  anfert.f -o rel64/anfert.o -I rel64

rel64/apex_day.o: apex_day.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  apex_day.f -o rel64/apex_day.o -I rel64

rel64/apply.o: apply.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  apply.f -o rel64/apply.o -I rel64

rel64/ascrv.o: ascrv.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ascrv.f -o rel64/ascrv.o -I rel64

rel64/atri.o: atri.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  atri.f -o rel64/atri.o -I rel64

rel64/aunif.o: aunif.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  aunif.f -o rel64/aunif.o -I rel64

rel64/autoirr.o: autoirr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  autoirr.f -o rel64/autoirr.o -I rel64

rel64/aveval.o: aveval.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  aveval.f -o rel64/aveval.o -I rel64

rel64/bacteria.o: bacteria.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  bacteria.f -o rel64/bacteria.o -I rel64

rel64/biofilm.o: biofilm.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  biofilm.f -o rel64/biofilm.o -I rel64

rel64/biozone.o: biozone.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} biozone.f -o rel64/biozone.o -I rel64

rel64/bmpfixed.o: bmpfixed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  bmpfixed.f -o rel64/bmpfixed.o -I rel64

rel64/bmpinit.o: bmpinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmpinit.f -o rel64/bmpinit.o -I rel64

rel64/bmp_det_pond.o: bmp_det_pond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmp_det_pond.f -o rel64/bmp_det_pond.o -I rel64

rel64/bmp_ri_pond.o: bmp_ri_pond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmp_ri_pond.f -o rel64/bmp_ri_pond.o -I rel64

rel64/bmp_sand_filter.o: bmp_sand_filter.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmp_sand_filter.f -o rel64/bmp_sand_filter.o -I rel64

rel64/bmp_sed_pond.o: bmp_sed_pond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmp_sed_pond.f -o rel64/bmp_sed_pond.o -I rel64

rel64/bmp_wet_pond.o: bmp_wet_pond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} bmp_wet_pond.f -o rel64/bmp_wet_pond.o -I rel64

rel64/buffer.o: buffer.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  buffer.f -o rel64/buffer.o -I rel64

rel64/burnop.o: burnop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  burnop.f -o rel64/burnop.o -I rel64

rel64/canopyint.o: canopyint.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  canopyint.f -o rel64/canopyint.o -I rel64

rel64/caps.o: caps.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  caps.f -o rel64/caps.o -I rel64

rel64/carbon_new.o: carbon_new.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} carbon_new.f -o rel64/carbon_new.o -I rel64

rel64/carbon_zhang2.o: carbon_zhang2.f90 rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFREE} carbon_zhang2.f90 -o rel64/carbon_zhang2.o -I rel64

rel64/cfactor.o: cfactor.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  cfactor.f -o rel64/cfactor.o -I rel64

rel64/check_wr.o: check_wr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  check_wr.f -o rel64/check_wr.o -I rel64

rel64/chkcst.o: chkcst.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  chkcst.f -o rel64/chkcst.o -I rel64

rel64/clgen.o: clgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  clgen.f -o rel64/clgen.o -I rel64

rel64/clicon.o: clicon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  clicon.f -o rel64/clicon.o -I rel64

rel64/command.o: command.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  command.f -o rel64/command.o -I rel64

rel64/conapply.o: conapply.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  conapply.f -o rel64/conapply.o -I rel64

rel64/confert.o: confert.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  confert.f -o rel64/confert.o -I rel64

rel64/crackflow.o: crackflow.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  crackflow.f -o rel64/crackflow.o -I rel64

rel64/crackvol.o: crackvol.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  crackvol.f -o rel64/crackvol.o -I rel64

rel64/curno.o: curno.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  curno.f -o rel64/curno.o -I rel64

rel64/dailycn.o: dailycn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  dailycn.f -o rel64/dailycn.o -I rel64

rel64/decay.o: decay.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  decay.f -o rel64/decay.o -I rel64

rel64/depstor.o: depstor.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  depstor.f -o rel64/depstor.o -I rel64

rel64/distrib_bmps.o: distrib_bmps.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} distrib_bmps.f -o rel64/distrib_bmps.o -I rel64

rel64/dormant.o: dormant.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  dormant.f -o rel64/dormant.o -I rel64

rel64/drains.o: drains.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  drains.f -o rel64/drains.o -I rel64

rel64/dstn1.o: dstn1.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  dstn1.f -o rel64/dstn1.o -I rel64

rel64/ee.o: ee.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ee.f -o rel64/ee.o -I rel64

rel64/eiusle.o: eiusle.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  eiusle.f -o rel64/eiusle.o -I rel64

rel64/enrsb.o: enrsb.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  enrsb.f -o rel64/enrsb.o -I rel64

rel64/erfc.o: erfc.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  erfc.f -o rel64/erfc.o -I rel64

rel64/estimate_ksat.o: estimate_ksat.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  estimate_ksat.f -o rel64/estimate_ksat.o -I rel64

rel64/etact.o: etact.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  etact.f -o rel64/etact.o -I rel64

rel64/etpot.o: etpot.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  etpot.f -o rel64/etpot.o -I rel64

rel64/expo.o: expo.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  expo.f -o rel64/expo.o -I rel64

rel64/fert.o: fert.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  fert.f -o rel64/fert.o -I rel64

rel64/filter.o: filter.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  filter.f -o rel64/filter.o -I rel64

rel64/filtw.o: filtw.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  filtw.f -o rel64/filtw.o -I rel64

rel64/finalbal.o: finalbal.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  finalbal.f -o rel64/finalbal.o -I rel64

rel64/gcycl.o: gcycl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  gcycl.f -o rel64/gcycl.o -I rel64

rel64/getallo.o: getallo.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  getallo.f -o rel64/getallo.o -I rel64

rel64/grass_wway.o: grass_wway.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  grass_wway.f -o rel64/grass_wway.o -I rel64

rel64/graze.o: graze.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  graze.f -o rel64/graze.o -I rel64

rel64/grow.o: grow.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  grow.f -o rel64/grow.o -I rel64

rel64/gwmod.o: gwmod.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  gwmod.f -o rel64/gwmod.o -I rel64

rel64/gwmod_deep.o: gwmod_deep.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  gwmod_deep.f -o rel64/gwmod_deep.o -I rel64

rel64/gwnutr.o: gwnutr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  gwnutr.f -o rel64/gwnutr.o -I rel64

rel64/gw_no3.o: gw_no3.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  gw_no3.f -o rel64/gw_no3.o -I rel64

rel64/h2omgt_init.o: h2omgt_init.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  h2omgt_init.f -o rel64/h2omgt_init.o -I rel64

rel64/harvestop.o: harvestop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  harvestop.f -o rel64/harvestop.o -I rel64

rel64/harvgrainop.o: harvgrainop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  harvgrainop.f -o rel64/harvgrainop.o -I rel64

rel64/harvkillop.o: harvkillop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  harvkillop.f -o rel64/harvkillop.o -I rel64

rel64/header.o: header.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  header.f -o rel64/header.o -I rel64

rel64/headout.o: headout.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  headout.f -o rel64/headout.o -I rel64

rel64/hhnoqual.o: hhnoqual.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hhnoqual.f -o rel64/hhnoqual.o -I rel64

rel64/hhwatqual.o: hhwatqual.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hhwatqual.f -o rel64/hhwatqual.o -I rel64

rel64/hmeas.o: hmeas.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hmeas.f -o rel64/hmeas.o -I rel64

rel64/hqdav.o: HQDAV.f90 rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  HQDAV.f90 -o rel64/hqdav.o -I rel64

rel64/hruaa.o: hruaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hruaa.f -o rel64/hruaa.o -I rel64

rel64/hruallo.o: hruallo.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hruallo.f -o rel64/hruallo.o -I rel64

rel64/hruday.o: hruday.f90 rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hruday.f90 -o rel64/hruday.o -I rel64

rel64/hrumon.o: hrumon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hrumon.f -o rel64/hrumon.o -I rel64

rel64/hrupond.o: hrupond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hrupond.f -o rel64/hrupond.o -I rel64

rel64/hrupondhr.o: hrupondhr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hrupondhr.f -o rel64/hrupondhr.o -I rel64

rel64/hruyr.o: hruyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hruyr.f -o rel64/hruyr.o -I rel64

rel64/hydroinit.o: hydroinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  hydroinit.f -o rel64/hydroinit.o -I rel64

rel64/icl.o: icl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  icl.f -o rel64/icl.o -I rel64

rel64/impndaa.o: impndaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  impndaa.f -o rel64/impndaa.o -I rel64

rel64/impndday.o: impndday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  impndday.f -o rel64/impndday.o -I rel64

rel64/impndmon.o: impndmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  impndmon.f -o rel64/impndmon.o -I rel64

rel64/impndyr.o: impndyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  impndyr.f -o rel64/impndyr.o -I rel64

rel64/impnd_init.o: impnd_init.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  impnd_init.f -o rel64/impnd_init.o -I rel64

rel64/irrigate.o: irrigate.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  irrigate.f -o rel64/irrigate.o -I rel64

rel64/irrsub.o: irrsub.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  irrsub.f -o rel64/irrsub.o -I rel64

rel64/irr_rch.o: irr_rch.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  irr_rch.f -o rel64/irr_rch.o -I rel64

rel64/irr_res.o: irr_res.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  irr_res.f -o rel64/irr_res.o -I rel64

rel64/jdt.o: jdt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  jdt.f -o rel64/jdt.o -I rel64

rel64/killop.o: killop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  killop.f -o rel64/killop.o -I rel64

rel64/lakeq.o: lakeq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lakeq.f -o rel64/lakeq.o -I rel64

rel64/latsed.o: latsed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  latsed.f -o rel64/latsed.o -I rel64

rel64/layersplit.o: layersplit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  layersplit.f -o rel64/layersplit.o -I rel64

rel64/lidinit.o: lidinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lidinit.f -o rel64/lidinit.o -I rel64

rel64/lids.o: lids.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lids.f -o rel64/lids.o -I rel64

rel64/lid_cistern.o: lid_cistern.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lid_cistern.f -o rel64/lid_cistern.o -I rel64

rel64/lid_greenroof.o: lid_greenroof.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lid_greenroof.f -o rel64/lid_greenroof.o -I rel64

rel64/lid_porpavement.o: lid_porpavement.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lid_porpavement.f -o rel64/lid_porpavement.o -I rel64

rel64/lid_raingarden.o: lid_raingarden.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lid_raingarden.f -o rel64/lid_raingarden.o -I rel64

rel64/log_normal.o: log_normal.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  log_normal.f -o rel64/log_normal.o -I rel64

rel64/lwqdef.o: lwqdef.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  lwqdef.f -o rel64/lwqdef.o -I rel64

rel64/main.o: main.f modparm.f
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} main.f -o rel64/main.o -J rel64

rel64/ncsed_leach.o: NCsed_leach.f90 rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  NCsed_leach.f90 -o rel64/ncsed_leach.o -I rel64

rel64/ndenit.o: ndenit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ndenit.f -o rel64/ndenit.o -I rel64

rel64/newtillmix.o: newtillmix.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  newtillmix.f -o rel64/newtillmix.o -I rel64

rel64/nfix.o: nfix.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nfix.f -o rel64/nfix.o -I rel64

rel64/nitvol.o: nitvol.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nitvol.f -o rel64/nitvol.o -I rel64

rel64/nlch.o: nlch.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nlch.f -o rel64/nlch.o -I rel64

rel64/nminrl.o: nminrl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nminrl.f -o rel64/nminrl.o -I rel64

rel64/noqual.o: noqual.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  noqual.f -o rel64/noqual.o -I rel64

rel64/npup.o: npup.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  npup.f -o rel64/npup.o -I rel64

rel64/nrain.o: nrain.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nrain.f -o rel64/nrain.o -I rel64

rel64/nup.o: nup.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nup.f -o rel64/nup.o -I rel64

rel64/nuts.o: nuts.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  nuts.f -o rel64/nuts.o -I rel64

rel64/openwth.o: openwth.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  openwth.f -o rel64/openwth.o -I rel64

rel64/operatn.o: operatn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  operatn.f -o rel64/operatn.o -I rel64

rel64/orgn.o: orgn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  orgn.f -o rel64/orgn.o -I rel64

rel64/orgncswat.o: orgncswat.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  orgncswat.f -o rel64/orgncswat.o -I rel64

rel64/origtile.o: origtile.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  origtile.f -o rel64/origtile.o -I rel64

rel64/ovr_sed.o: ovr_sed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} ovr_sed.f -o rel64/ovr_sed.o -I rel64

rel64/percmacro.o: percmacro.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  percmacro.f -o rel64/percmacro.o -I rel64

rel64/percmain.o: percmain.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} percmain.f -o rel64/percmain.o -I rel64

rel64/percmicro.o: percmicro.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  percmicro.f -o rel64/percmicro.o -I rel64

rel64/pestlch.o: pestlch.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pestlch.f -o rel64/pestlch.o -I rel64

rel64/pestw.o: pestw.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pestw.f -o rel64/pestw.o -I rel64

rel64/pesty.o: pesty.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pesty.f -o rel64/pesty.o -I rel64

rel64/pgen.o: pgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pgen.f -o rel64/pgen.o -I rel64

rel64/pgenhr.o: pgenhr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pgenhr.f -o rel64/pgenhr.o -I rel64

rel64/pkq.o: pkq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pkq.f -o rel64/pkq.o -I rel64

rel64/plantmod.o: plantmod.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  plantmod.f -o rel64/plantmod.o -I rel64

rel64/plantop.o: plantop.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  plantop.f -o rel64/plantop.o -I rel64

rel64/pmeas.o: pmeas.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pmeas.f -o rel64/pmeas.o -I rel64

rel64/pminrl.o: pminrl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pminrl.f -o rel64/pminrl.o -I rel64

rel64/pminrl2.o: pminrl2.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pminrl2.f -o rel64/pminrl2.o -I rel64

rel64/pond.o: pond.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pond.f -o rel64/pond.o -I rel64

rel64/pondhr.o: pondhr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  pondhr.f -o rel64/pondhr.o -I rel64

rel64/pothole.o: pothole.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} pothole.f -o rel64/pothole.o -I rel64

rel64/potholehr.o: potholehr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} potholehr.f -o rel64/potholehr.o -I rel64

rel64/print_hyd.o: print_hyd.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  print_hyd.f -o rel64/print_hyd.o -I rel64

rel64/psed.o: psed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  psed.f -o rel64/psed.o -I rel64

rel64/qman.o: qman.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  qman.f -o rel64/qman.o -I rel64

rel64/ran1.o: ran1.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ran1.f -o rel64/ran1.o -I rel64

rel64/rchaa.o: rchaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rchaa.f -o rel64/rchaa.o -I rel64

rel64/rchday.o: rchday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rchday.f -o rel64/rchday.o -I rel64

rel64/rchinit.o: rchinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rchinit.f -o rel64/rchinit.o -I rel64

rel64/rchmon.o: rchmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rchmon.f -o rel64/rchmon.o -I rel64

rel64/rchuse.o: rchuse.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} rchuse.f -o rel64/rchuse.o -I rel64

rel64/rchyr.o: rchyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} rchyr.f -o rel64/rchyr.o -I rel64

rel64/reachout.o: reachout.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} reachout.f -o rel64/reachout.o -I rel64

rel64/readatmodep.o: readatmodep.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} readatmodep.f -o rel64/readatmodep.o -I rel64

rel64/readbsn.o: readbsn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} readbsn.f -o rel64/readbsn.o -I rel64

rel64/readchm.o: readchm.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} readchm.f -o rel64/readchm.o -I rel64

rel64/readcnst.o: readcnst.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} readcnst.f -o rel64/readcnst.o -I rel64

rel64/readfcst.o: readfcst.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readfcst.f -o rel64/readfcst.o -I rel64

rel64/readfert.o: readfert.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readfert.f -o rel64/readfert.o -I rel64

rel64/readfig.o: readfig.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readfig.f -o rel64/readfig.o -I rel64

rel64/readfile.o: readfile.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readfile.f -o rel64/readfile.o -I rel64

rel64/readgw.o: readgw.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readgw.f -o rel64/readgw.o -I rel64

rel64/readhru.o: readhru.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readhru.f -o rel64/readhru.o -I rel64

rel64/readinpt.o: readinpt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readinpt.f -o rel64/readinpt.o -I rel64

rel64/readlup.o: readlup.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readlup.f -o rel64/readlup.o -I rel64

rel64/readlwq.o: readlwq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readlwq.f -o rel64/readlwq.o -I rel64

rel64/readmgt.o: readmgt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readmgt.f -o rel64/readmgt.o -I rel64

rel64/readmon.o: readmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readmon.f -o rel64/readmon.o -I rel64

rel64/readops.o: readops.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readops.f -o rel64/readops.o -I rel64

rel64/readpest.o: readpest.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readpest.f -o rel64/readpest.o -I rel64

rel64/readplant.o: readplant.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readplant.f -o rel64/readplant.o -I rel64

rel64/readpnd.o: readpnd.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readpnd.f -o rel64/readpnd.o -I rel64

rel64/readres.o: readres.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readres.f -o rel64/readres.o -I rel64

rel64/readrte.o: readrte.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readrte.f -o rel64/readrte.o -I rel64

rel64/readru.o: readru.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readru.f -o rel64/readru.o -I rel64

rel64/readsdr.o: readsdr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readsdr.f -o rel64/readsdr.o -I rel64

rel64/readsepticbz.o: readsepticbz.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readsepticbz.f -o rel64/readsepticbz.o -I rel64

rel64/readseptwq.o: readseptwq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readseptwq.f -o rel64/readseptwq.o -I rel64

rel64/readsno.o: readsno.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readsno.f -o rel64/readsno.o -I rel64

rel64/readsol.o: readsol.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readsol.f -o rel64/readsol.o -I rel64

rel64/readsub.o: readsub.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readsub.f -o rel64/readsub.o -I rel64

rel64/readswq.o: readswq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readswq.f -o rel64/readswq.o -I rel64

rel64/readtill.o: readtill.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readtill.f -o rel64/readtill.o -I rel64

rel64/readwr.o: readwr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readwr.f -o rel64/readwr.o -I rel64
	
rel64/readhruwr.o: readhruwr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readhruwr.f -o rel64/readhruwr.o -I rel64

rel64/readstrwr.o: readstrwr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readstrwr.f -o rel64/readstrwr.o -I rel64

rel64/readurban.o: readurban.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readurban.f -o rel64/readurban.o -I rel64

rel64/readwgn.o: readwgn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readwgn.f -o rel64/readwgn.o -I rel64

rel64/readwus.o: readwus.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readwus.f -o rel64/readwus.o -I rel64

rel64/readwwq.o: readwwq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readwwq.f -o rel64/readwwq.o -I rel64

rel64/readyr.o: readyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  readyr.f -o rel64/readyr.o -I rel64

rel64/reccnst.o: reccnst.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  reccnst.f -o rel64/reccnst.o -I rel64

rel64/recday.o: recday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  recday.f -o rel64/recday.o -I rel64

rel64/rechour.o: rechour.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rechour.f -o rel64/rechour.o -I rel64

rel64/recmon.o: recmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} recmon.f -o rel64/recmon.o -I rel64

rel64/recyear.o: recyear.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  recyear.f -o rel64/recyear.o -I rel64

rel64/regres.o: regres.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  regres.f -o rel64/regres.o -I rel64

rel64/res.o: res.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  res.f -o rel64/res.o -I rel64

rel64/resbact.o: resbact.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  resbact.f -o rel64/resbact.o -I rel64

rel64/resetlu.o: resetlu.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  resetlu.f -o rel64/resetlu.o -I rel64

rel64/reshr.o: reshr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  reshr.f -o rel64/reshr.o -I rel64

rel64/resinit.o: resinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  resinit.f -o rel64/resinit.o -I rel64

rel64/resnut.o: resnut.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  resnut.f -o rel64/resnut.o -I rel64

rel64/rewind_init.o: rewind_init.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rewind_init.f -o rel64/rewind_init.o -I rel64

rel64/rhgen.o: rhgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rhgen.f -o rel64/rhgen.o -I rel64

rel64/rootfr.o: rootfr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rootfr.f -o rel64/rootfr.o -I rel64

rel64/route.o: route.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  route.f -o rel64/route.o -I rel64

rel64/routels.o: routels.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  routels.f -o rel64/routels.o -I rel64

rel64/routeunit.o: routeunit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  routeunit.f -o rel64/routeunit.o -I rel64

rel64/routres.o: routres.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  routres.f -o rel64/routres.o -I rel64

rel64/rsedaa.o: rsedaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rsedaa.f -o rel64/rsedaa.o -I rel64

rel64/rseday.o: rseday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rseday.f -o rel64/rseday.o -I rel64

rel64/rsedmon.o: rsedmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rsedmon.f -o rel64/rsedmon.o -I rel64

rel64/rsedyr.o: rsedyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rsedyr.f -o rel64/rsedyr.o -I rel64

rel64/rtbact.o: rtbact.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtbact.f -o rel64/rtbact.o -I rel64

rel64/rtday.o: rtday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtday.f -o rel64/rtday.o -I rel64

rel64/rteinit.o: rteinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rteinit.f -o rel64/rteinit.o -I rel64

rel64/rthmusk.o: rthmusk.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rthmusk.f -o rel64/rthmusk.o -I rel64

rel64/rthpest.o: rthpest.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rthpest.f -o rel64/rthpest.o -I rel64

rel64/rthsed.o: rthsed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} rthsed.f -o rel64/rthsed.o -I rel64

rel64/rthvsc.o: rthvsc.f90 rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rthvsc.f90 -o rel64/rthvsc.o -I rel64

rel64/rtmusk.o: rtmusk.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtmusk.f -o rel64/rtmusk.o -I rel64

rel64/rtout.o: rtout.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtout.f -o rel64/rtout.o -I rel64

rel64/rtpest.o: rtpest.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtpest.f -o rel64/rtpest.o -I rel64

rel64/rtsed.o: rtsed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtsed.f -o rel64/rtsed.o -I rel64

rel64/rtsed_bagnold.o: rtsed_bagnold.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtsed_bagnold.f -o rel64/rtsed_bagnold.o -I rel64

rel64/rtsed_kodatie.o: rtsed_kodatie.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtsed_kodatie.f -o rel64/rtsed_kodatie.o -I rel64

rel64/rtsed_molinas_wu.o: rtsed_Molinas_Wu.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtsed_Molinas_Wu.f -o rel64/rtsed_molinas_wu.o -I rel64

rel64/rtsed_yangsand.o: rtsed_yangsand.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  rtsed_yangsand.f -o rel64/rtsed_yangsand.o -I rel64

rel64/sat_excess.o: sat_excess.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sat_excess.f -o rel64/sat_excess.o -I rel64

rel64/save.o: save.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  save.f -o rel64/save.o -I rel64

rel64/saveconc.o: saveconc.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  saveconc.f -o rel64/saveconc.o -I rel64

rel64/schedule_ops.o: schedule_ops.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  schedule_ops.f -o rel64/schedule_ops.o -I rel64

rel64/sched_mgt.o: sched_mgt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sched_mgt.f -o rel64/sched_mgt.o -I rel64

rel64/set_wrprior.o: set_wrprior.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  set_wrprior.f -o rel64/set_wrprior.o -I rel64

rel64/simulate.o: simulate.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  simulate.f -o rel64/simulate.o -I rel64

rel64/sim_initday.o: sim_initday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sim_initday.f -o rel64/sim_initday.o -I rel64

rel64/sim_inityr.o: sim_inityr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sim_inityr.f -o rel64/sim_inityr.o -I rel64

rel64/slrgen.o: slrgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  slrgen.f -o rel64/slrgen.o -I rel64

rel64/smeas.o: smeas.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  smeas.f -o rel64/smeas.o -I rel64

rel64/snom.o: snom.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  snom.f -o rel64/snom.o -I rel64

rel64/soil_chem.o: soil_chem.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  soil_chem.f -o rel64/soil_chem.o -I rel64

rel64/soil_par.o: soil_par.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  soil_par.f -o rel64/soil_par.o -I rel64

rel64/soil_phys.o: soil_phys.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  soil_phys.f -o rel64/soil_phys.o -I rel64

rel64/soil_write.o: soil_write.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  soil_write.f -o rel64/soil_write.o -I rel64

rel64/solp.o: solp.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  solp.f -o rel64/solp.o -I rel64

rel64/solt.o: solt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  solt.f -o rel64/solt.o -I rel64

rel64/std1.o: std1.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  std1.f -o rel64/std1.o -I rel64

rel64/std2.o: std2.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  std2.f -o rel64/std2.o -I rel64

rel64/std3.o: std3.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  std3.f -o rel64/std3.o -I rel64

rel64/stdaa.o: stdaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  stdaa.f -o rel64/stdaa.o -I rel64

rel64/storeinitial.o: storeinitial.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  storeinitial.f -o rel64/storeinitial.o -I rel64

rel64/structure.o: structure.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  structure.f -o rel64/structure.o -I rel64

rel64/subaa.o: subaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  subaa.f -o rel64/subaa.o -I rel64

rel64/subbasin.o: subbasin.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  subbasin.f -o rel64/subbasin.o -I rel64

rel64/subday.o: subday.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  subday.f -o rel64/subday.o -I rel64

rel64/submon.o: submon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  submon.f -o rel64/submon.o -I rel64

rel64/substor.o: substor.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  substor.f -o rel64/substor.o -I rel64

rel64/subwq.o: subwq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  subwq.f -o rel64/subwq.o -I rel64

rel64/subyr.o: subyr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  subyr.f -o rel64/subyr.o -I rel64

rel64/sub_subbasin.o: sub_subbasin.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sub_subbasin.f -o rel64/sub_subbasin.o -I rel64

rel64/sumhyd.o: sumhyd.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sumhyd.f -o rel64/sumhyd.o -I rel64

rel64/sumv.o: sumv.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sumv.f -o rel64/sumv.o -I rel64

rel64/surface.o: surface.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  surface.f -o rel64/surface.o -I rel64

rel64/surfstor.o: surfstor.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  surfstor.f -o rel64/surfstor.o -I rel64

rel64/surfst_h2o.o: surfst_h2o.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  surfst_h2o.f -o rel64/surfst_h2o.o -I rel64

rel64/surq_daycn.o: surq_daycn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  surq_daycn.f -o rel64/surq_daycn.o -I rel64

rel64/surq_greenampt.o: surq_greenampt.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  surq_greenampt.f -o rel64/surq_greenampt.o -I rel64

rel64/swbl.o: swbl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  swbl.f -o rel64/swbl.o -I rel64

rel64/sweep.o: sweep.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sweep.f -o rel64/sweep.o -I rel64

rel64/swu.o: swu.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  swu.f -o rel64/swu.o -I rel64

rel64/sw_init.o: sw_init.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  sw_init.f -o rel64/sw_init.o -I rel64

rel64/tair.o: tair.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tair.f -o rel64/tair.o -I rel64

rel64/tgen.o: tgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tgen.f -o rel64/tgen.o -I rel64

rel64/theta.o: theta.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  theta.f -o rel64/theta.o -I rel64

rel64/tillfactor.o: tillfactor.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tillfactor.f -o rel64/tillfactor.o -I rel64

rel64/tillmix.o: tillmix.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tillmix.f -o rel64/tillmix.o -I rel64

rel64/tmeas.o: tmeas.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tmeas.f -o rel64/tmeas.o -I rel64

rel64/tran.o: tran.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tran.f -o rel64/tran.o -I rel64

rel64/transfer.o: transfer.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  transfer.f -o rel64/transfer.o -I rel64

rel64/tstr.o: tstr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  tstr.f -o rel64/tstr.o -I rel64

rel64/ttcoef.o: ttcoef.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ttcoef.f -o rel64/ttcoef.o -I rel64

rel64/ttcoef_wway.o: ttcoef_wway.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ttcoef_wway.f -o rel64/ttcoef_wway.o -I rel64

rel64/urban.o: urban.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  urban.f -o rel64/urban.o -I rel64

rel64/urbanhr.o: urbanhr.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  urbanhr.f -o rel64/urbanhr.o -I rel64

rel64/urb_bmp.o: urb_bmp.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  urb_bmp.f -o rel64/urb_bmp.o -I rel64

rel64/varinit.o: varinit.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  varinit.f -o rel64/varinit.o -I rel64

rel64/vbl.o: vbl.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  vbl.f -o rel64/vbl.o -I rel64

rel64/virtual.o: virtual.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG} ${LONGFIX} virtual.f -o rel64/virtual.o -I rel64

rel64/volq.o: volq.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  volq.f -o rel64/volq.o -I rel64

rel64/washp.o: washp.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  washp.f -o rel64/washp.o -I rel64

rel64/watbal.o: watbal.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  watbal.f -o rel64/watbal.o -I rel64

rel64/water_hru.o: water_hru.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  water_hru.f -o rel64/water_hru.o -I rel64

rel64/watqual.o: watqual.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  watqual.f -o rel64/watqual.o -I rel64

rel64/watqual2.o: watqual2.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  watqual2.f -o rel64/watqual2.o -I rel64

rel64/wattable.o: wattable.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  wattable.f -o rel64/wattable.o -I rel64

rel64/watuse.o: watuse.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  watuse.f -o rel64/watuse.o -I rel64

rel64/weatgn.o: weatgn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  weatgn.f -o rel64/weatgn.o -I rel64

rel64/wetlan.o: wetlan.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  wetlan.f -o rel64/wetlan.o -I rel64

rel64/wmeas.o: wmeas.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  wmeas.f -o rel64/wmeas.o -I rel64

rel64/wndgen.o: wndgen.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  wndgen.f -o rel64/wndgen.o -I rel64

rel64/writea.o: writea.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  writea.f -o rel64/writea.o -I rel64

rel64/writeaa.o: writeaa.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  writeaa.f -o rel64/writeaa.o -I rel64

rel64/writed.o: writed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  writed.f -o rel64/writed.o -I rel64

rel64/writem.o: writem.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  writem.f -o rel64/writem.o -I rel64

rel64/xmon.o: xmon.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  xmon.f -o rel64/xmon.o -I rel64

rel64/ysed.o: ysed.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  ysed.f -o rel64/ysed.o -I rel64

rel64/zero0.o: zero0.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  zero0.f -o rel64/zero0.o -I rel64

rel64/zero1.o: zero1.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  zero1.f -o rel64/zero1.o -I rel64

rel64/zero2.o: zero2.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  zero2.f -o rel64/zero2.o -I rel64

rel64/zeroini.o: zeroini.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  zeroini.f -o rel64/zeroini.o -I rel64

rel64/zero_urbn.o: zero_urbn.f rel64/main.o
	${FC} ${ARCH64} ${FFLAG} ${RFLAG}  zero_urbn.f -o rel64/zero_urbn.o -I rel64

rel64_clean:
	rm -f ${NAMEREL64}.exe
	rm -f rel64/*.o
	rm -f rel64/*.mod
	rm -f rel64/*~

