#include <stdint.h>
#include "main.h"
#include "adclib.h"
#include "user_tim.h"

void USER_ADC_Init(void) {
    // Enable ADC and GPIOA clocks
    RCC->IOPENR |= (1 << 0);     // GPIOAEN
    RCC->APBENR2 |= (1 << 20);   // ADCEN

    // PA0 analog mode
    GPIOA->MODER |= (0x3 << (0*2));
    GPIOA->PUPDR &= ~(0x3 << (0*2));

    // Configure CKMODE for synchronous clock divided by 2
    ADC1->CFGR2 &= ~(0x3 << 30);

    ADC->CCR &= ~(0xE << 18);
    ADC->CCR |=  (0x1 << 18);

    // Configure resolution, alignment, conversion mode
    ADC1->CFGR1 &= ~(0x1 << 13); // Single conversion mode
    ADC1->CFGR1 &= ~(0x1 << 5);  // Right alignment
    ADC1->CFGR1 &= ~(0x3 << 3);  // 12-bit resolution

    // Sampling time = shortest
    ADC1->SMPR |= ~(0x7 << 0);

    ADC1->ISR &= ~(0x1UL << 13U);
    ADC1->CFGR1 &= ~(0x1UL << 21U) & ~(0x1UL << 2U);

    // Select channel 0 (PA0)
    ADC1->CHSELR |= (1 << 0);

    while (!(ADC1->ISR & (0x1UL << 13U)));

    // Enable internal regulator
    ADC1->CR |= (1 << 28);       
    USER_TIM14_Delay(1);

    // Calibration
    while (!USER_ADC_Calibration());

    // Enable ADC
    ADC1->CR |= (1 << 0);         
    for (uint32_t i = 0; i < 1000 && !(ADC1->ISR & (1 << 0)); i++) USER_TIM14_Delay(1);
    if (!(ADC1->ISR & (1 << 0))) return;
}

uint8_t USER_ADC_Calibration(void) {
    ADC1->CR |= (1 << 31);                   
    while (ADC1->CR & (1 << 31));            

    if (ADC1->CALFACT > 0x7F) {
        ADC1->CALFACT = 0x7F;
    }
    return 1;
}

uint16_t USER_ADC_Read(void) {
    ADC1->CR |= (1 << 2);               
    while (!(ADC1->ISR & (1 << 2)));    
    if (ADC1->ISR & (1 << 4)) {         
        ADC1->ISR |= (1 << 4);          
    }
    return (uint16_t)(ADC1->DR);        
}
