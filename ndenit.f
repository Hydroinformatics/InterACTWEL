      subroutine ndenit(k,j,cdg,wdn,void)
!!    this subroutine computes denitrification 

	use parm, NDENIT_FROM_MODULE_PARM => ndenit !Added by MBS, 6/12/2020 to address the compilation error "'ndenit' of module 'parm', imported at (1), is also the name of the current program unit"
      
	integer :: k,j
	real*8 :: cdg, wdn, void

      wdn = 0.
	vof = 1./(1.+(void/0.04)**5)
	wdn =sol_no3(k,j)*(1.-Exp(-cdn(j)*cdg*vof*sol_cbn(k,j)))
	sol_no3(k,j) = sol_no3(k,j) - wdn

	return
	end