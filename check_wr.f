      subroutine check_wr(jj,vmm)

          use parm
    
          integer :: jj
          integer :: wrid
          real*8 :: vmm2, cnv2, wrdiff, vmm

          vmm2 = 999999.

          cnv = 0.
          cnv = hru_ha(jj) * 10.
          cnv2 = 35.3147 * (1./43560.)

          wrid = hruwr(jj)
          wrdiff = depthwr(wrid,curyr)


          if (((vmm * cnv * cnv2) + hruwra(wrid,curyr)) > wrdiff) then 
            vmm2 = wrdiff - hruwra(wrid,curyr)
            vmm2 = (vmm2/cnv)*(43560.0/35.3147)
            if (vmm2 < 0.01) then vmm2 = 0.
          end if
          
          !!strdate = wrstrdate(wrid,curyr)
          !!enddate = wrendate(wrid,curyr)
          !!if (wrdate < strdate .and. wrdate > enddate) then
          !!  vmm2 = 0.
          !!end if

          vmm = Min(vmm2, vmm)

        !!if (jj==1) then
        !!if (wrid==1050 .or. wrid==1051) then
        !! WRITE(*,*) jj
        !!  WRITE(*,*) wrid, depthwr(wrid,curyr), hruwra(wrid,curyr), vmm
        !!  endif 
        !!endif 

      return
      end