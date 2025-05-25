#include <stdint.h>
#include "main.h"
#include "user_uart.h"

// Prototype for function to receive a byte via UART1
uint8_t USER_UART1_Receive_8bit(void);

// Initializes UART1 peripheral and associated pins
void USER_UART1_Init(void) {
	// Enable clock for GPIOA
	RCC->IOPENR = RCC->IOPENR | (0x1UL << 0U);
	// Enable clock for USART1
	RCC->APBENR2 = RCC->APBENR2 | (0x1UL << 14U);

	// Configure PA9 (TX) as alternate function AF1, no pull-up/pull-down, push-pull, alternate mode
	GPIOA->AFRH = GPIOA->AFRH & ~(0xEUL << 4U);   // Clear AF bits for PA9
	GPIOA->AFRH = GPIOA->AFRH | (0x1UL << 4U);    // Select AF1 for PA9
	GPIOA->PUPDR = GPIOA->PUPDR & ~(0x3UL << 18U);// No pull-up/pull-down on PA9
	GPIOA->OTYPER = GPIOA->OTYPER & ~(0x1UL << 9U);// Push-pull on PA9
	GPIOA->MODER = GPIOA->MODER & ~(0x1UL << 18U);// Clear mode for PA9
	GPIOA->MODER = GPIOA->MODER | (0x2UL << 18U); // Alternate mode for PA9

	// Configure PA10 (RX) as alternate function AF1, no pull-up/pull-down, push-pull, alternate mode
	GPIOA->AFRH = GPIOA->AFRH & ~(0xEUL << 8U);   // Clear AF bits for PA10
	GPIOA->AFRH = GPIOA->AFRH | (0x1UL << 8U);    // Select AF1 for PA10
	GPIOA->PUPDR = GPIOA->PUPDR & ~(0x3UL << 20U);// No pull-up/pull-down on PA10
	GPIOA->OTYPER = GPIOA->OTYPER & ~(0x1UL << 10U);// Push-pull on PA10
	GPIOA->MODER = GPIOA->MODER & ~(0x1UL << 20U);// Clear mode for PA10
	GPIOA->MODER = GPIOA->MODER | (0x2UL << 20U); // Alternate mode for PA10

	// USART1 configuration
	USART1->CR1 = USART1->CR1 & ~(0x1UL << 28U);  // Disable LIN mode
	USART1->CR1 = USART1->CR1 & ~(0x1UL << 12U);  // 8 data bits
	USART1->BRR = 5000;                            // Baudrate (example: 115200 @ 48MHz)
	USART1->CR2 = USART1->CR2 & ~(0x3UL << 12U);  // 1 stop bit
	USART1->CR1 = USART1->CR1 | (0x1UL << 0U);    // Enable USART1
	USART1->CR1 = USART1->CR1 | (0x1UL << 3U);    // Enable transmission
	USART1->CR1 = USART1->CR1 | (0x1UL << 2U);    // Enable reception
}

// Sends a byte via USART1
void USER_USART1_Send_8bit(uint8_t Data) {
	while (!(USART1->ISR & (0x1UL << 7U))); // Wait until transmit register is empty
	USART1->TDR = Data;                     // Write data to transmit
}

// Sends a data buffer via USART1
void USER_USART1_Transmit(uint8_t *pData, uint16_t size) {
	for (int i = 0; i < size; i++) {
		USER_USART1_Send_8bit(*pData++);    // Send each byte from buffer
	}
}

// Redefinition of _write function for printf/standard output redirection
int _write(int file, char *ptr, int len) {
	int DataIdx;
	for (DataIdx = 0; DataIdx < len; DataIdx++) {
		while (!(USART1->ISR & (0x1UL << 7U))); // Wait until transmit register is empty
		USART1->TDR = *ptr++;                   // Send next byte
	}
	return len;                                 // Return number of bytes sent
}

// Receives a byte via USART1 if data is available
uint8_t USER_UART1_Receive_8bit(void) {
	if ((USART1->ISR & (0x1UL << 5U))) {        // If data received
		return (uint8_t)USART1->RDR;            // Return received data
	} else {
		return '0';                             // If no data, return '0'
	}
}


void USER_USART1_Send_String(const char *str) {
    while (*str) {
        USER_USART1_Send_8bit(*str++); // Envía cada carácter
    }
}