      subroutine readhruwr

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    this subroutine reads input data from water rights (watrgt.dat)

!!    ~ ~ ~ INCOMING VARIABLES ~ ~ ~
!!    name        |units         |definition
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
!!            |none          |
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

!!    ~ ~ ~ OUTGOING VARIABLES ~ ~ ~
!!    name        |units         |definition
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
!!    deptwr(:)   |acres-ft          |Total depth of water right
!!    wrid        |NA                |Water right IDs
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

!!    ~ ~ ~ LOCAL DEFINITIONS ~ ~ ~
!!    name        |units         |definition
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
!!    eof         |none          |end of file flag
!!    it          |none          |counter which represents the array 
!!                               |storage number of the tillage data
!!                               |the array storage number is used by the
!!                               |model to access data for a specific
!!                               |tillage operation
!!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

!!    ~ ~ ~ ~ ~ ~ END SPECIFICATIONS ~ ~ ~ ~ ~ ~

      use parm

      integer :: eof, hruid, wsrc, wridi, pwr, pwrhru
      integer :: rowc, subid
!!    real :: dwr
      !!character (len=4) :: hruids, wrsrcs, wridis, pwrs
      character (len=100) :: line

      eof = 0
      !!WRITE(*,*) "Reading HRU+WR"
      rowc = 1
      pwr = 1

      do
        wsrc = 0
        hruid = 0
        pwrhru = 0
        wridi = 0
        subid = 0
        !!hruids = ""
        !!line = ""

        read (206,5050,iostat=eof) hruid, wridi, wsrc, subid, pwrhru
        
        if (eof < 0) exit

        if (hruid == 0) exit
        
        !! Assumes the list of HRUs is in order of priority date
        hruwr_dict(rowc,1) = hruid
        hruwr_dict(rowc,2) = wridi
        hruwr_dict(rowc,3) = wsrc
        hruwr_dict(rowc,4) = pwrhru
        hruwr_dict(rowc,5) = subid

        if (pwrhru == 1) then
            maxhruwrpr(hruid) = pwrhru
        elseif (pwrhru > maxhruwrpr(hruid)) then
            maxhruwrpr(hruid) = pwrhru
        endif

        !!hruwruse_dict(rowc,1) = hrudi
        !!hruwruse_dict(rowc,2) = wridi
        hruwruse_dict(rowc) = 0.0

        if (pwrhru == 1) then
	    
            hruwr(hruid) = wridi
            hruwrsrc(hruid) = wsrc
            !!hruwrprior(hruid) = pwrhru
	    !!if (pwr == hruid) then
		!!WRITE(*,*) pwr, hruid, wridi, wsrc, subid, pwrhru
	    !!end if
            priorwr(pwr) = hruid
	    
            if (wsrc > 0) then
                  irr_sc(hruid) = wsrc
                  irr_no(hruid) = subid
                  irr_sca(hruid) = wsrc
                  irr_noa(hruid) = subid
            end if

            pwr = pwr + 1
            
        end if

        rowc = rowc + 1

      end do
      WRITE(*,*) "Total HRU", pwr
      
      bool_priorwr = 0
      temp_priorwr = priorwr
      hruwr_org = hruwr
      hruwrsrc_org = hruwrsrc

      close (206)
      return
 5050 format (i6,3x,i6,3x,i4,3x,i4,3x,i4)
      end