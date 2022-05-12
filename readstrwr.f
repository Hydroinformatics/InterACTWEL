      subroutine readstrwr

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

      integer :: eof, istrd, subid, wrstd, wrend
      real*8 :: wrflow
      character (len=20) :: line
    
      eof = 0

      do 
        wrflow = 0.
        subid = 0
        wrstd = 0
        wrend = 0

      read (208,5060, iostat=eof) subid, wrflow, wrstd, wrend

      if (eof < 0) exit

      !if (wrflow > 0) then
       do istrd = wrstd, wrend
        flowmin_wr(subid,istrd) = wrflow
        !!WRITE(*,*) subid, istrd, flowmin_wr(subid,istrd)
       end do
      !else
      !  do i = 1, 365
      !  flowmin_wr(subid,i) = wrflow
      !  end do
      !endif 
      end do

      close (208)
      return
 5060 format (i6,3x,f6.0,3x,i4,3x,i4)
      end