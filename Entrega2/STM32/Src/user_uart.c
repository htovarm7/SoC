	#include <stdint.h>
#include "main.h"
#include "user_uart.h"

static void USER_USART1_Send_8bit( uint8_t Data );
uint8_t USER_UART1_Receive_8bit( void );

void USER_UART1_Init( void ){
	RCC->IOPENR = RCC->IOPENR  | (0x1UL << 0U);
	RCC->APBENR2 = RCC->APBENR2 | (0x1UL << 14U);

	GPIOA->AFRH = GPIOA->AFRH & ~(0xEUL << 4U);
	GPIOA->AFRH = GPIOA->AFRH | (0x1UL << 4U);
	GPIOA->PUPDR = GPIOA->PUPDR & ~(0x3UL << 18U);
	GPIOA->OTYPER = GPIOA->OTYPER & ~(0x1UL << 9U);
	GPIOA->MODER = GPIOA->MODER & ~(0x1UL << 18U);
	GPIOA->MODER = GPIOA->MODER | (0x2UL << 18U);

	GPIOA->AFRH = GPIOA->AFRH & ~(0xEUL << 8U);
	GPIOA->AFRH = GPIOA->AFRH | (0x1UL << 8U);
	GPIOA->PUPDR = GPIOA->PUPDR & ~(0x3UL << 20U);
	GPIOA->OTYPER = GPIOA->OTYPER & ~(0x1UL << 10U);
	GPIOA->MODER = GPIOA->MODER & ~(0x1UL << 20U);
	GPIOA->MODER = GPIOA->MODER | (0x2UL << 20U);

	USART1->CR1 = USART1->CR1 & ~(0x1UL << 28U);
	USART1->CR1 = USART1->CR1 & ~(0x1UL << 12U);
	USART1->BRR = 5000;
	USART1->CR2 = USART1->CR2 & ~(0x3UL << 12U);
	USART1->CR1 = USART1->CR1 | (0x1UL << 0U);
	USART1->CR1 = USART1->CR1 | (0x1UL << 3U);
	USART1->CR1 = USART1->CR1 | (0x1UL << 2U);
}

static void USER_USART1_Send_8bit( uint8_t Data ){
	while(!( USART1->ISR & ( 0x1UL <<  7U)));
	USART1->TDR = Data;
}

void USER_USART1_Transmit( uint8_t *pData, uint16_t size ){
	for( int i = 0; i < size; i++ ){
		USER_USART1_Send_8bit( *pData++ );
	}
}

int _write(int file, char *ptr, int len){
	int DataIdx;
	for(DataIdx=0; DataIdx<len; DataIdx++){
		while(!( USART1->ISR & (0x1UL << 7U)));
		USART1->TDR = *ptr++;
	}
	return len;
}

uint8_t USER_UART1_Receive_8bit( void ){
	if((USART1->ISR & (0x1UL << 5U))){
		return (uint8_t)USART1->RDR;
	}
	else{
		return '0';
	}
}
