      subroutine readwr

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

      integer :: eof, wr, wsrc
      integer :: wrstd, wrend, wyr
      integer :: icf, dyr
      integer :: dwr
      !!character (len=20) :: line

      eof = 0
  
      read (207,'(A)',iostat=eof) line
      
      do 
        dwr = 0.
        wr = 0
        wyr = 0
        wsrc = 0
        wrstd = 0
        wrend = 0
        
        read (207,5090,iostat=eof) wyr, wr, wsrc, dwr, wrstd, wrend

        wr = int(wr)
        wyr = int(wyr)

        if (eof < 0) exit

        if (wyr > 0) then
          wrsrc(wr,wyr) = int(wsrc)
          depthwr(wr,wyr) = dwr
          wrstdate(wr,wyr) = int(wrstd)
          wrendate(wr,wyr) = int(wrend)
          hruwra(wr,wyr) = 0.
        endif
      end do

      close (207)
      
      return
 5090 format (i4,3x,i5,3x,i4,3x,i6,3x,i4,3x,i4)
      end