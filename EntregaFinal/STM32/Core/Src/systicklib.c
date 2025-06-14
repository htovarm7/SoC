#include <stdint.h>
#include "main.h"
#include "systicklib.h"

// Initializes the SysTick timer for 1ms intervals
void USER_SysTick_Init( void ){
  Systick->RVR  = 48000 - 1; // Load value for 1ms (assuming 48MHz clock)
  Systick->CVR  = 0;         // Reset the counter
  Systick->CSR |=  ( 0x1UL <<  2U ); // Select processor clock as SysTick clock source
}

// Delays for 'time' milliseconds using SysTick
void SysTick_Delay( uint32_t time ) {
  Systick->CSR |=  ( 0x1UL <<  0U ); // Start SysTick
  for(uint32_t i = 0; i < time; i++){
    // Wait until COUNTFLAG is set (when the timer overflows)
    while(!( Systick->CSR & ( 0x1UL << 16U )));
  }
  Systick->CSR &= ~( 0x1UL <<  0U ); // Stop SysTick
}
