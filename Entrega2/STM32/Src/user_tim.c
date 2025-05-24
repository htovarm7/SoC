#include <stdint.h>
#include "main.h"
#include "user_tim.h"

void USER_TIM3_Init( void ){
	RCC->APBENR1	|=  ( 0x1UL <<  1U );
	TIM3->SMCR		&= ~( 0x1UL << 16U )
					&  ~( 0x7UL <<  0U );
	TIM3->CR1		&= ~( 0x1UL <<  7U )
					&  ~( 0x3UL <<  5U )
					&  ~( 0x1UL <<  4U )
					&  ~( 0x1UL <<  1U );
}

void USER_TIM3_Delay( uint16_t prescaler, uint16_t maxCount ){
	TIM3->PSC = prescaler;
	TIM3->ARR = maxCount;
	TIM3->SR &= ~( 0x1UL << 0U );
	TIM3->CR1 |= ( 0x1UL << 0U );
	while(!(TIM3->SR & ( 0x1UL << 0U )));
	TIM3->CR1 &= ~( 0x1UL << 0U );
}
