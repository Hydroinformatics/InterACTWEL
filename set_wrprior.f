      subroutine set_wrprior(temphru, temppwrid)
      
    !!    ~ ~ ~ PURPOSE ~ ~ ~
    !!    this subroutine defines the priority of hrus 
    !!    given the info. from the water rights.
    !!    Needs review: Change so that even if the
    !!    wr for the current hru does not have more water
    !!    the hru can use the next wr in their list (if available)

          use parm
    
          integer :: irow, temphru, pwrc, cpwrhru
          integer :: hruid, wsrc, wridi, temppwrid
          integer :: subidi, pwrhru, cwridi
          integer :: tprior

          cpwrhru = -1 

          hruwrprior = temp_priorwr
          
          if (temppwrid < 9999) then

          do irow = 1, uhruwr
            hruid = hruwr_dict(irow,1)
            wridi = hruwr_dict(irow,2)
            if (hruid == temphru .and. wridi == temppwrid) then
              cpwrhru = hruwr_dict(irow,4)
            end if
          end do
          
          tprior = (cpwrhru + 1)
          if (tprior > maxhruwrpr(temphru)) then
            cpwrhru = -1 
          endif

          !!WRITE(*,*) temphru

          if (cpwrhru > 0) then

          pwrc = 1
          do irow = 1, uhruwr
              
            hruid = hruwr_dict(irow,1)
            wridi = hruwr_dict(irow,2)
            wsrci = hruwr_dict(irow,3)
            pwrhru = hruwr_dict(irow,4)
            subidi = hruwr_dict(irow,5)

            !!WRITE(*,*) "O", irow, pwrc, hruid, wridi, temphru, tprior

            !!cpwrhru = hruwrprior(hruid)
            !!cwridi = hruwr(hruid)

            !!if (hruid == temphru .and. pwrhru == temppwrid) then
            !!    hruwrprior(hruid) = temppwr + 1
            !!end if

            !!if (hruid == temphru .and. pwrhru == (temppwr + 1)) then
            !!  hruwr(hruid) = hruwr_dict(irow,2)
            !!  hruwrsrc(hruid) = hruwr_dict(irow,3)
            !!end if

            if (hruid == temphru .and. pwrhru == tprior) then !! Had to break up because of length (compiler)
              !!WRITE(*,*) "P", irow, pwrc, hruid, wridi
              !!if (pwrhru == (cpwrhru + 1)) then
                !!WRITE(*,*) "Set WR Prior", hruid, wridi
                
                !if (pwrc /= hruid) then
                !  call exit()
                !end if

                hruwr(hruid) = wridi
                hruwrsrc(hruid) = wsrci
                hruwrprior(pwrc) = hruid
                pwrc = pwrc + 1

                if (wsrci > 0) then
                  irr_sc(hruid) = wsrci
                  irr_no(hruid) = subidi
                  irr_sca(hruid) = wsrci
                  irr_noa(hruid) = subidi
                end if
              
              !!else
              !!  hruwrprior(pwrc) = hruid
              !!  pwrc = pwrc + 1
              !!end if
            
            !else if (hruid == temphru .and. hruwr(hruid) == ) then 

            else

              !WRITE(*,*) "N", irow, pwrc, hruid, wridi
              if (hruid /= temphru .and. hruwr(hruid) == wridi) then
                
                !if (pwrc /= hruid) then
                !  call exit()
                !end if
                !!WRITE(*,*) "N", irow, pwrc, hruid
                hruwrprior(pwrc) = hruid
                pwrc = pwrc + 1
              end if
            end if

          end do

          end if 
          end if

          temp_priorwr = hruwrprior

          !! priorwr = temp_priorwr
          return
          end