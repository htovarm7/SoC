/* Libraries, Definitions and Global Declarations */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "main.h"
#include "user_uart.h"
#include "FreeRTOSConfig.h"
#include "FreeRTOS.h"
#include "task.h"
#include "user_tim.h"
#include "exti_func.h"
#include "adclib.h"
#include "lcd.h"

#define BUFFER_SIZE 8

char buffer_str[8];
char buffer_vel[8];
char buffer_rpm[8];
char buffer_gear[8];
int velocity = 0;
int index_k = 0;

uint8_t button_status = 0;
uint16_t val;

void USER_RCC_Init(void);
void System_init(void);
void USER_GPIO_Init(void);
void USART1_IRQHandler(void);

TaskHandle_t Task1Handle;
TaskHandle_t Task2Handle;
TaskHandle_t Task3Handle;
TaskHandle_t Task4Handle;

void StartTask1(void *pvParameters);
void StartTask2(void *pvParameters);
void StartTask3(void *pvParameters);
void StartTask4(void *pvParameters);

/* Main entry point */
int main(void)
{
	HAL_Init();
	System_init();

	// Create FreeRTOS tasks with different priorities
	xTaskCreate(StartTask1, "Task1", 128, NULL, 1, &Task1Handle);
	xTaskCreate(StartTask2, "Task2", 128, NULL, 3, &Task2Handle);
	xTaskCreate(StartTask3, "Task3", 128, NULL, 2, &Task3Handle);
	xTaskCreate(StartTask4, "Task4", 128, NULL, 4, &Task4Handle);

	vTaskStartScheduler();

	// Should never reach here
	for(;;) {}
}

// Task1: Reads ADC value and button status
void StartTask1(void *pvParameters) {
	for(;;) {
		val = USER_ADC_Read();
		// Read button status from PA7
		if (GPIOA->IDR & (0x1UL << 7U)) {
			button_status = 1;
		} else {
			button_status = 0;
		}
		vTaskDelay(6);
	}
}

// Task2: Updates LCD display with velocity, gear, and RPM
void StartTask2(void *pvParameters) {
	vTaskDelay(2);
	for(;;) {
		LCD_Set_Cursor(1, 1);
		LCD_Put_Str("Vel:       G:  ");
		LCD_Set_Cursor(1, 5);
		LCD_Put_Str(buffer_vel);
		LCD_Set_Cursor(1, 14);
		LCD_Put_Str(buffer_gear);
		LCD_Set_Cursor(2, 1);
		LCD_Put_Str("RPM:       ");
		LCD_Set_Cursor(2, 5);
		LCD_Put_Str(buffer_rpm);
		vTaskDelay(6);
	}
}

// Task3: Prints ADC value and button status via UART
void StartTask3(void *pvParameters) {
	vTaskDelay(1);
	for(;;) {
		printf("{adc: %u, button: %u}\n", val, button_status);
		vTaskDelay(6);
	}
}

// Task4: Updates PWM cycles based on velocity
void StartTask4(void *pvParameters) {
	vTaskDelay(5);
	for(;;) {
		if(velocity > 50) {
			velocity = 50;
		}
		update_cycle(velocity, 1);
		update_cycle(velocity, 2);
		update_cycle(velocity, 3);
		update_cycle(velocity, 4);
		vTaskDelay(5);
	}
}

// System initialization: clocks, UART, GPIO, timers, ADC, LCD
void System_init(void){
	USER_RCC_Init();
	USER_UART1_Init();
	USER_UART2_Init();
	USER_GPIO_Init();
	USER_TIM14_Init();
	USER_TIM3_PWM_Init();
	USER_ADC_Init();
	LCD_Init();
	LCD_Clear();
}

// USART1 interrupt handler: parses incoming data for velocity, RPM, and gear
void USART1_IRQHandler(void) {
	if ((USART1->ISR & (0x1UL << 5U))) { // Data received
		char received = USART1->RDR;
		if (received == 'V') {
			velocity = atoi(buffer_str);
			memcpy(buffer_vel, buffer_str, sizeof(buffer_str));
			memset(buffer_str, 0, sizeof(buffer_str));
			index_k = 0;
		} else if (received == 'S') {
			memcpy(buffer_rpm, buffer_str, sizeof(buffer_str));
			memset(buffer_str, 0, sizeof(buffer_str));
			index_k = 0;
		} else if (received == 'E') {
			memcpy(buffer_gear, buffer_str, sizeof(buffer_str));
			memset(buffer_str, 0, sizeof(buffer_str));
			index_k = 0;
		} else {
			if (index_k < BUFFER_SIZE - 1) {
				buffer_str[index_k++] = received;
			} else {
				memset(buffer_str, 0, sizeof(buffer_str));
				index_k = 0;
			}
		}
	}
}

// GPIO initialization: configure PA9 as input with pull-down
void USER_GPIO_Init(void)
{
	GPIOA->MODER &= ~(0x3UL << 14U);   // Set PA9 as input
	GPIOA->PUPDR &= ~(0x1UL << 14U);   // Clear pull-up
	GPIOA->PUPDR |= (0x2UL << 14U);    // Set pull-down
}

// RCC initialization: configure system clock to 48 MHz
void USER_RCC_Init(void){
	FLASH->ACR &= ~(0x6UL << 0U);      // Clear latency bits
	FLASH->ACR |=  (0x1UL << 0U);      // Set 2 HCLK cycles latency
	while((FLASH->ACR & (0x7UL << 0U)) != 0x001UL); // Wait for latency
	RCC->CR &= ~(0x7UL << 11U);        // HSISYS division factor by 1
	while(!(RCC->CR & (0x1UL << 10U))); // Wait for HSISYS ready
	RCC->CFGR &= ~(0x7UL << 0U);       // Select HSISYS as SYSCLK
	RCC->CFGR &= ~(0x1UL << 11U);      // HCLK division factor by 1
	SystemCoreClock = 48000000;
}
