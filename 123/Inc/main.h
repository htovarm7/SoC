#ifndef MAIN_H_
#define MAIN_H_

//void Tarea_Lectura_ADC(void);
//void Tarea_Lectura_Boton(void);
//void Tarea_LCD_Display(void);
//void Tarea_Control_Ciclo(void);

/* Embedded FLASH memory registers */
typedef struct
{
	volatile uint32_t ACR;
	volatile uint32_t RESERVED1;
	volatile uint32_t KEYR;
	volatile uint32_t OPTKEYR;
	volatile uint32_t SR;
	volatile uint32_t CR;
	volatile uint32_t RESERVED2[2];
	volatile uint32_t OPTR;
	volatile uint32_t PCROP1ASR;
	volatile uint32_t PCROP1AER;
	volatile uint32_t WRP1AR;
	volatile uint32_t WRP1BR;
	volatile uint32_t PCROP1BSR;
	volatile uint32_t PCROP1BER;
	volatile uint32_t RESERVED3[17];
	volatile uint32_t SECR;
} FLASH_TypeDef;

/* Reset and Clock Control registers */
typedef struct
{
	volatile uint32_t CR;
	volatile uint32_t ICSCR;
	volatile uint32_t CFGR;
	volatile uint32_t RESERVED[3];
	volatile uint32_t CIER;
	volatile uint32_t CIFR;
	volatile uint32_t CICR;
	volatile uint32_t IOPRSTR;
	volatile uint32_t AHBRSTR;
	volatile uint32_t APBRSTR1;
	volatile uint32_t APBRSTR2;
	volatile uint32_t IOPENR;
	volatile uint32_t AHBENR;
  volatile uint32_t APBENR1;
  volatile uint32_t APBENR2;
} RCC_TypeDef;

/* General Purpose I/O registers */
typedef struct
{
	volatile uint32_t MODER;
	volatile uint32_t OTYPER;
	volatile uint32_t OSPEEDR;
	volatile uint32_t PUPDR;
	volatile uint32_t IDR;
	volatile uint32_t ODR;
	volatile uint32_t BSRR;
	volatile uint32_t LCKR;
  volatile uint32_t AFRL;
	volatile uint32_t AFRH;
  volatile uint32_t BRR;
} GPIO_TypeDef;

#define RCC_BASE	  0x40021000UL//		RCC base address
#define FLASH_BASE	0x40022000UL//		FLASH base address
#define GPIOA_BASE	0x50000000UL//		GPIO Port A base address
#define GPIOB_BASE  0x50000400UL //   GPIO Port B base address

#define USART1_BASE 0x40013800UL
#define USART2_BASE 0x40004400UL
#define TIM3_BASE	0x40000400UL
#define TIM14_BASE  0x40002000UL
#define TIM16_BASE	0x40014400UL
#define TIM17_BASE  0x40014800UL

#define RCC     (( RCC_TypeDef *)RCC_BASE )
#define FLASH	(( FLASH_TypeDef	*)FLASH_BASE )
#define GPIOA		(( GPIO_TypeDef *)GPIOA_BASE )
#define GPIOB		(( GPIO_TypeDef *)GPIOB_BASE )
#define USART1  (( USART_TypeDef *)USART1_BASE )
#define USART2  (( USART_TypeDef *)USART2_BASE )
#define TIM3    (( TIM_TypeDef * )TIM3_BASE )
#define TIM14   (( TIM_TypeDef *) TIM14_BASE )
#define TIM16   (( TIM_TypeDef * )TIM16_BASE )
#define TIM17   (( TIM_TypeDef * )TIM17_BASE )

#endif /* MAIN_H_ */
