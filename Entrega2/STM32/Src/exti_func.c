#include <stdint.h>
#include "main.h"
#include "systicklib.h"
#include "exti_func.h"

void USER_EXTI1_Init( void ){
  // Enable interrupt on line 25
  EXTI->IMR1    |=  (  0x1UL <<  25U );

  // Disable event generation on line 25
  EXTI->EMR1    &=  ~(  0x1UL <<  25U );

  // Enable EXTI1 interrupt vector

  // Set interrupt priority (no changes)
  NVIC->IPR[6]  &= ~( 0x00UL <<  3U );

  // NVIC->ISER    |=  (  0x1UL <<  16U ); // Commented line: enable interrupt at position 16

  // Enable interrupt at position 27 in NVIC
  NVIC->ISER    |=  (  0x1UL <<  27U );

}
