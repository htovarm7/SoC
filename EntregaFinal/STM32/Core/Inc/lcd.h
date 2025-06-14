#ifndef INC_LCD_H_
#define INC_LCD_H_

// Pin definitions
#define LCD_RS_PIN_HIGH       ( 0x1UL <<  9U )  // Set RS_LCD (PB9)
#define LCD_RW_PIN_HIGH       ( 0x1UL << 10U )  // Set RW_LCD (PB10)
#define LCD_EN_PIN_HIGH       ( 0x1UL << 11U )  // Set EN_LCD (PB11)

#define LCD_RS_PIN_LOW        ( 0x1UL << 25U )  // Reset RS_LCD (PB9)
#define LCD_RW_PIN_LOW        ( 0x1UL << 26U )  // Reset RW_LCD (PB10)
#define LCD_EN_PIN_LOW        ( 0x1UL << 27U )  // Reset EN_LCD (PB11)

#define LCD_D4_PIN_HIGH       ( 0x1UL << 12U )  // Set DATA4_LCD (PB12)
#define LCD_D5_PIN_HIGH       ( 0x1UL << 13U )  // Set DATA5_LCD (PB13)
#define LCD_D6_PIN_HIGH       ( 0x1UL << 14U )  // Set DATA6_LCD (PB14)
#define LCD_D7_PIN_HIGH       ( 0x1UL << 15U )  // Set DATA7_LCD (PB15)

#define LCD_D4_PIN_LOW        ( 0x1UL << 28U )  // Reset DATA4_LCD (PB12)
#define LCD_D5_PIN_LOW        ( 0x1UL << 29U )  // Reset DATA5_LCD (PB13)
#define LCD_D6_PIN_LOW        ( 0x1UL << 30U )  // Reset DATA6_LCD (PB14)
#define LCD_D7_PIN_LOW        ( 0x1UL << 31U )  // Reset DATA7_LCD (PB15)

// LCD command macros
#define LCD_Clear()           LCD_Write_Cmd(0x01U)
#define LCD_Display_ON()      LCD_Write_Cmd(0x0EU)
#define LCD_Display_OFF()     LCD_Write_Cmd(0x08U)
#define LCD_Cursor_Home()     LCD_Write_Cmd(0x02U)
#define LCD_Cursor_Blink()    LCD_Write_Cmd(0x0FU)
#define LCD_Cursor_ON()       LCD_Write_Cmd(0x0EU)
#define LCD_Cursor_OFF()      LCD_Write_Cmd(0x0CU)
#define LCD_Cursor_Left()     LCD_Write_Cmd(0x10U)
#define LCD_Cursor_Right()    LCD_Write_Cmd(0x14U)
#define LCD_Cursor_SLeft()    LCD_Write_Cmd(0x18U)
#define LCD_Cursor_SRight()   LCD_Write_Cmd(0x1CU)

// Function prototypes
void LCD_Data_Out4(uint8_t val);
void LCD_Write_Byte(uint8_t val);
void LCD_Write_Cmd(uint8_t val);
void LCD_Put_Char(uint8_t c);
void LCD_Init(void);
void LCD_Set_Cursor(uint8_t line, uint8_t column);
void LCD_Put_Str(char *str);
void LCD_Put_Num(int16_t num);
char LCD_Busy(void);
void LCD_Pulse_EN(void);
void LCD_BarGraphic(int16_t value, int16_t size);
void LCD_BarGraphicXY(int16_t pos_x, int16_t pos_y, int16_t value);

#endif /* INC_LCD_H_ */
