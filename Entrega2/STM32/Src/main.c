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

	GPIOB->ODR |= (1UL << 0U); // PB0
	GPIOB->ODR |= (1UL << 1U); // PB1
	GPIOB->ODR |= (1UL << 2U); // PB2
	GPIOA->ODR |= (1UL << 6U); // PA6

	uint16_t val = 0, prev_val = 0xFFFF;
	uint8_t button_status = 0, prev_button = 0xFF;

	LCD_Clear();

	for(;;) {
	    val = USER_ADC_Read();
		// Update_LEDs(val);

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

void USER_GPIO_Init(void){
    // Configurar PA6 y PA7 como salida
    GPIOA->MODER &= ~((0x3UL << (6U * 2)) | (0x3UL << (7U * 2))); // Limpiar bits
    GPIOA->MODER |=  ((0x1UL << (6U * 2)) | (0x1UL << (7U * 2))); // Salida
    GPIOA->OTYPER &= ~((0x1UL << 6U) | (0x1UL << 7U));            // Push-pull
    GPIOA->PUPDR  &= ~((0x3UL << (6U * 2)) | (0x3UL << (7U * 2))); // Sin pull

    // Encender PA6 y PA7
    GPIOA->ODR |= (1UL << 6U) | (1UL << 7U);

    // Configurar PB0, PB1 y PB2 como salida
    GPIOB->MODER &= ~((0x3UL << (0U * 2)) | (0x3UL << (1U * 2)) | (0x3UL << (2U * 2))); // Limpiar
    GPIOB->MODER |=  ((0x1UL << (0U * 2)) | (0x1UL << (1U * 2)) | (0x1UL << (2U * 2))); // Salida
    GPIOB->OTYPER &= ~((0x1UL << 0U) | (0x1UL << 1U) | (0x1UL << 2U));                 // Push-pull
    GPIOB->PUPDR  &= ~((0x3UL << (0U * 2)) | (0x3UL << (1U * 2)) | (0x3UL << (2U * 2))); // Sin pull

    // Encender PB0, PB1 y PB2
    GPIOB->ODR |= (1UL << 0U) | (1UL << 1U) | (1UL << 2U);

    // Configurar PA8 como entrada con pull-down
    GPIOA->MODER &= ~(0x3UL << 16U); // PA8 como entrada
    GPIOA->PUPDR &= ~(0x3UL << 16U); // Limpiar pull
    GPIOA->PUPDR |=  (0x2UL << 16U); // Pull-down
}

// void Update_LEDs(uint16_t adc_val){
//     // Limpiar todos los LEDs
//     GPIOA->ODR &= ~((1UL << 6U) | (1UL << 7U));              // PA6 y PA7
//     GPIOB->ODR &= ~((1UL << 0U) | (1UL << 1U) | (1UL << 2U)); // PB0, PB1, PB2

//     if (adc_val > 683)  GPIOB->ODR |= (1UL << 0U); // LED 1
//     if (adc_val > 1365) GPIOB->ODR |= (1UL << 1U); // LED 2
//     if (adc_val > 2048) GPIOB->ODR |= (1UL << 2U); // LED 3
//     if (adc_val > 2730) GPIOA->ODR |= (1UL << 6U); // LED 4
//     if (adc_val > 3412) GPIOA->ODR |= (1UL << 7U); // LED 5
// }
