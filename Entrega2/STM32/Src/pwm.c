//#include <stdint.h>
//#include "main.h"
//#include "user_tim.h"
//#include "pwm.h"
//
//void PWM_Init(void) {
//    // 1. Activar reloj de GPIOA, GPIOB y TIM3
//    RCC->IOPENR |= (1 << 0) | (1 << 1); // GPIOA y GPIOB
//    RCC->APBENR1 |= (1 << 1);           // TIM3 EN
//
//    // 2. Configurar PA6, PA7 como alternate function (AF1 para TIM3)
//    GPIOA->MODER &= ~((3 << (6*2)) | (3 << (7*2)));
//    GPIOA->MODER |=  ((2 << (6*2)) | (2 << (7*2)));
//    GPIOA->AFRL &= ~((0xF << (6*4)) | (0xF << (7*4)));  // Changed AFR[0] to AFRL
//    GPIOA->AFRL |=  ((1 << (6*4)) | (1 << (7*4)));     // AF1 para TIM3
//
//    // Configurar PB0, PB1 como alternate function (AF1 para TIM3)
//    GPIOB->MODER &= ~((3 << (0*2)) | (3 << (1*2)));
//    GPIOB->MODER |=  ((2 << (0*2)) | (2 << (1*2)));
//    GPIOB->AFRL &= ~((0xF << (0*4)) | (0 << (1*4)));  // Changed to GPIOB and AFRL
//    GPIOB->AFRL |=  ((1 << (0*4)) | (1 << (1*4)));     // AF1 para TIM3
//
//    // 3. Configurar TIM3 para PWM
//    TIM3->PSC = 47;      // Prescaler: fCK_PSC = 1 MHz (si fCK = 48 MHz)
//    TIM3->ARR = 1000;    // Periodo PWM = 1 ms → 1 kHz
//
//    // PWM mode 1 en CH1-CH4 con preload habilitado
//    TIM3->CCMR1 |= (6 << 4) | (1 << 3);   // CH1
//    TIM3->CCMR1 |= (6 << 12) | (1 << 11); // CH2
//    TIM3->CCMR2 |= (6 << 4) | (1 << 3);   // CH3
//    TIM3->CCMR2 |= (6 << 12) | (1 << 11); // CH4
//
//    // Habilitar salida en los 4 canales
//    TIM3->CCER |= (1 << 0) | (1 << 4) | (1 << 8) | (1 << 12);
//
//    // Habilitar auto-reload preload y contador
//    TIM3->CR1 |= (1 << 7); // ARPE
//    TIM3->CR1 |= (1 << 0); // CEN (Enable counter)
//}
//
//void PWM_Set_Intensity_From_ADC(uint16_t adc_value) {
//    if (adc_value > 4095) adc_value = 4095;
//    uint16_t duty = (adc_value * 1000) / 4095; // Mapea 0–4095 a 0–1000
//
//    TIM3->CCR1 = duty;  // LED 1
//    TIM3->CCR2 = duty;  // LED 2
//    TIM3->CCR3 = duty;  // LED 3
//    TIM3->CCR4 = duty;  // LED 4
//}
