      subroutine allocatewr(jj,vmm)
      
    !!    ~ ~ ~ PURPOSE ~ ~ ~
    !!    this subroutine calculates the total water used
    !!    for a given water right
    
    !!    ~ ~ ~ INCOMING VARIABLES ~ ~ ~
    !!    name        |units         |definition
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    !!    aairr(:)    |mm H2O        |average annual amount of irrigation water
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    
    !!    ~ ~ ~ OUTGOING VARIABLES ~ ~ ~
    !!    name        |units         |definition
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    !!    aairr(:)    |mm H2O        |average annual amount of irrigation water
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    
    !!    ~ ~ ~ LOCAL DEFINITIONS ~ ~ ~
    !!    name        |units         |definition
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    !!    volmm       |mm H2O        |depth irrigation water applied to HRU
    !!    jj          |none          |HRU number
    !!    ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    
    !!    ~ ~ ~ ~ ~ ~ END SPECIFICATIONS ~ ~ ~ ~ ~ ~
    
          use parm
    
          integer :: jj
          real :: vmm
          real :: cnv, cnv2

          cnv = 0.
          cnv = hru_ha(jj) * 10.

          cnv2 = 0.
          cnv2 = 35.3147 * (1./43560.)

          !!if (jj == 632) then
          !!  WRITE(*,*) "Alloc-1: ", jj, hruwr(jj), hruwra(hruwr(jj))
          !!end if

          hruwra(hruwr(jj)) =  hruwra(hruwr(jj)) + (vmm * cnv * cnv2)
          
          !!if (jj == 632) then
          !!WRITE(*,*) "Alloc-2: ", jj, (vmm * cnv * cnv2)
          !!end if

          return
          end