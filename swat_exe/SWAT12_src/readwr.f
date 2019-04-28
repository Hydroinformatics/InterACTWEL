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

      integer :: eof, wr, wsrc, wrstd, wrend
!! drainmod tile equations  - addition random roughness 06/2006
      real :: dwr
      character (len=20) :: line

      eof = 0

      do 
        dwr = 0.
        wr = 0
        wsrc = 0
        wrstd = 0
        wrend = 0

        !!read (207,'(A)',iostat=eof) line
        !!WRITE(*,*) line
        read (207,5050,iostat=eof) wr, wsrc, dwr, wrstd, wrend
        !!read (line,5050) wr, dwr
        !!WRITE(*,*) wr, wsrc, dwr, wrstd, wrend

        if (eof < 0) exit

        if (wr == 0) exit

        wrsrc(wr) = wsrc
        depthwr(wr) = dwr
        wrstrdate(wr) = wrstd
        wrendate(wr) = wrend
        hruwra(wr) = 0.

      end do

      close (207)
      return
 5050 format (i4,3x,i4,3x,f4.0,3x,i4,3x,i4)
      end