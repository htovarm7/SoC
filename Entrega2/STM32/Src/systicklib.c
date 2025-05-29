#include <stdint.h>
#include "main.h"
#include "systicklib.h"

void USER_SysTick_Init(void) {
  Systick->RVR  = 48000 - 1;          
  Systick->CVR  = 0;                   
  Systick->CSR |= (0x1UL << 2U);       
}

void SysTick_Delay(uint32_t time) {
  Systick->CSR |= (0x1UL << 0U);       
  for(uint32_t i = 0; i < time; i++) {
    while(!(Systick->CSR & (0x1UL << 16U)));
  }
  Systick->CSR &= ~(0x1UL << 0U);
}
