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

      integer :: eof, hruid, wsrc, wridi, pwr
!! drainmod tile equations  - addition random roughness 06/2006
!!    real :: dwr
      !!character (len=4) :: hruids, wrsrcs, wridis, pwrs
      character (len=100) :: line

      eof = 0
      !!WRITE(*,*) "Reading HRU+WR"
      do
        wsrc = 0
        pwr = 0
        wr = 0
        hruid = 0
        !!hruids = ""
        line = ""

        !!read (206,'(A)',iostat=eof) line
        !!WRITE(*,*) line
        read (206,5050) pwr, wridi, wsrc, hruid
        !!WRITE(*,*) hruid, wridi, wrsrc, pwr
        
        if (eof < 0) exit

        if (pwr == 0) exit
        

        hruwr(hruid) = wridi
        hruwrsrc(hruid) = wsrc
        priorwr(pwr) = hruid
        

      end do

      close (206)
      return
 5050 format (i4,4x,i4,4x,i4,4x,i4)
      end