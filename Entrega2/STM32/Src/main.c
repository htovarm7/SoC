#include <stdint.h>
#include "main.h"
#include "user_tim.h"
#include "user_uart.h"
#include "lcd.h"
#include "systicklib.h"
#include "adclib.h"

int main(void)
{
	// Initialize system clock and peripherals
	USER_RCC_Init();
	USER_SysTick_Init();
	USER_UART1_Init();
	USER_GPIO_Init();
	LCD_Init();
	USER_ADC_Init();

	uint16_t val = 0, prev_val = 0xFFFF;
	uint8_t button_status = 0, prev_button = 0xFF;

	LCD_Clear();

	for(;;) {
	    val = USER_ADC_Read();

	    if(GPIOA->IDR & (0x1UL << 8U)){
	        button_status = 1;
	    } else {
	        button_status = 0;
	    }

	    // Solo actualiza si el valor cambió
	    if (val != prev_val) {
	        LCD_Set_Cursor(1, 1);
	        LCD_Put_Str("ADC:      ");  // Borrar valor anterior (rellenar con espacios)
	        LCD_Set_Cursor(1, 6);       // Solo el número
	        LCD_Put_Num(val);
	        prev_val = val;
	    }

	    if (button_status != prev_button) {
	        LCD_Set_Cursor(2, 1);
	        LCD_Put_Str("Button:   ");
	        LCD_Set_Cursor(2, 9);
	        LCD_Put_Num(button_status);
	        prev_button = button_status;
	    }

	    // Enviar UART (si lo necesitas)
	    USER_USART1_Send_8bit(button_status);

	    SysTick_Delay(50);  // Una pequeña pausa para evitar sobrecarga
	}
}

// Configure system clock and enable GPIOA peripheral
void USER_RCC_Init(void){
		RCC->IOPENR |= (0x1UL << 0U); // Enable GPIOA clock

		// Flash latency and clock setup
		FLASH->ACR &= ~(0x6UL << 0U);
		FLASH->ACR |=  (0x1UL << 0U);
		while((FLASH->ACR & (0x7UL << 0U)) != 0x001UL);

		RCC->CR &= ~(0x7UL << 11U);
		while(!(RCC->CR & (0x1UL << 10U)));

		RCC->CFGR &= ~(0x7UL << 0U);
		RCC->CFGR &= ~(0x1UL << 11U);
}

// Configure PA5 as output (LED), PA8 as input with pull-down (button)
void USER_GPIO_Init(void){
		// // PA5 as output (LED)
		// GPIOA->MODER &= ~(0x3UL << (5U * 2)); // Clear mode bits
		// GPIOA->MODER |=  (0x1UL << (5U * 2)); // Set as output
		// GPIOA->OTYPER &= ~(0x1UL << 5U);      // Push-pull
		// GPIOA->PUPDR  &= ~(0x3UL << (5U * 2)); // No pull-up/down
		// GPIOA->ODR &= ~(0x1UL << 5U);         // LED off initially

		// PA8 as input with pull-down
		GPIOA->MODER &= ~(0x3UL << 16U); // Set PA8 as input
		GPIOA->PUPDR &= ~(0x3UL << 16U); // Clear pull-up/down
		GPIOA->PUPDR |=  (0x2UL << 16U); // Enable pull-down
}
