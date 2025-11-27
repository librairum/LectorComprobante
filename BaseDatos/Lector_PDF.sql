USE [Proyecto_PPP]
GO
/****** Object:  Table [dbo].[Operaciones]    Script Date: 24/11/2025 23:35:30 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Operaciones](
	[OperacionID] [int] IDENTITY(1,1) NOT NULL,
	[Tipo] [varchar](30) NOT NULL,
	[NombreArchivo] [nvarchar](255) NOT NULL,
	[RutaArchivo] [nvarchar](400) NOT NULL,
	[Estado] [varchar](20) NOT NULL,
	[FechaCreacion] [datetime] NOT NULL,
	[UsuarioID] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[OperacionID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Usuarios]    Script Date: 24/11/2025 23:35:30 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Usuarios](
	[UsuarioID] [int] IDENTITY(1,1) NOT NULL,
	[NombreCompleto] [nvarchar](100) NOT NULL,
	[CorreoElectronico] [nvarchar](150) NOT NULL,
	[Contrasena] [nvarchar](255) NOT NULL,
	[FechaRegistro] [datetime] NULL,
	[UltimoAcceso] [datetime] NULL,
	[Estado] [varchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[UsuarioID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO
SET IDENTITY_INSERT [dbo].[Operaciones] ON 
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (1, N'PDF', N'FE-_2_14.01.23._hostal_ancash_huarmey.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\FE-_2_14.01.23._hostal_ancash_huarmey.pdf', N'CREADO', CAST(N'2025-10-26T22:17:55.667' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (2, N'PDF', N'FE-_2_14.01.23._hostal_ancash_huarmey.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\FE-_2_14.01.23._hostal_ancash_huarmey.pdf', N'PROCESADO', CAST(N'2025-10-26T22:17:57.273' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (3, N'EXPORTACION', N'resultados_facturas_20251026_221759.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\resultados_facturas_20251026_221759.xlsx', N'EXPORTADO', CAST(N'2025-10-26T22:17:59.743' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (4, N'PDF', N'FE-2.2_160223Metro_llave_francesa.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\FE-2.2_160223Metro_llave_francesa.pdf', N'CREADO', CAST(N'2025-10-27T02:03:19.180' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (5, N'PDF', N'FE-2.2_160223Metro_llave_francesa.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\FE-2.2_160223Metro_llave_francesa.pdf', N'PROCESADO', CAST(N'2025-10-27T02:03:37.653' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (6, N'EXPORTACION', N'resultados_facturas_20251027_020345.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\resultados_facturas_20251027_020345.xlsx', N'EXPORTADO', CAST(N'2025-10-27T02:03:45.763' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (7, N'PDF', N'documento0038.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\documento0038.pdf', N'CREADO', CAST(N'2025-11-14T20:24:22.270' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (8, N'PDF', N'documento0038.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\documento0038.pdf', N'PROCESADO', CAST(N'2025-11-14T20:24:25.460' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (9, N'EXPORTACION', N'resultados_facturas_20251114_202429.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\resultados_facturas_20251114_202429.xlsx', N'EXPORTADO', CAST(N'2025-11-14T20:24:30.440' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (10, N'PDF', N'10442132777-01-FF11-1251_15092025.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\10442132777-01-FF11-1251_15092025.pdf', N'CREADO', CAST(N'2025-11-14T20:27:16.070' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (11, N'PDF', N'10442132777-01-FF11-1251_15092025.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\10442132777-01-FF11-1251_15092025.pdf', N'PROCESADO', CAST(N'2025-11-14T20:27:18.433' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (12, N'EXPORTACION', N'resultados_facturas_20251114_202720.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\resultados_facturas_20251114_202720.xlsx', N'EXPORTADO', CAST(N'2025-11-14T20:27:20.693' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (13, N'PDF_EMISOR', N'20420310383-01-F003-00007890.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_20420310383-01-F003-00007890.pdf', N'CREADO', CAST(N'2025-11-24T17:20:59.850' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (14, N'EMISOR', N'emisor_20420310383-01-F003-00007890.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_20420310383-01-F003-00007890.pdf', N'PROCESADO', CAST(N'2025-11-24T17:21:06.430' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (15, N'EXPORTACION', N'emisores_20251124_172111.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\emisores_20251124_172111.xlsx', N'EXPORTADO', CAST(N'2025-11-24T17:21:11.300' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (16, N'PDF_EMISOR', N'10442132777-01-FF11-1251_15092025_1.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_10442132777-01-FF11-1251_15092025_1.pdf', N'CREADO', CAST(N'2025-11-24T23:18:00.253' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (17, N'EMISOR', N'emisor_10442132777-01-FF11-1251_15092025_1.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_10442132777-01-FF11-1251_15092025_1.pdf', N'PROCESADO', CAST(N'2025-11-24T23:18:08.677' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (18, N'EXPORTACION', N'emisores_20251124_231814.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\emisores_20251124_231814.xlsx', N'EXPORTADO', CAST(N'2025-11-24T23:18:14.273' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (19, N'PDF_EMISOR', N'documento0003.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_documento0003.pdf', N'CREADO', CAST(N'2025-11-24T23:20:37.870' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (20, N'EMISOR', N'emisor_documento0003.pdf', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\uploads\emisor_documento0003.pdf', N'PROCESADO', CAST(N'2025-11-24T23:20:45.070' AS DateTime), 1)
GO
INSERT [dbo].[Operaciones] ([OperacionID], [Tipo], [NombreArchivo], [RutaArchivo], [Estado], [FechaCreacion], [UsuarioID]) VALUES (21, N'EXPORTACION', N'emisores_20251124_232049.xlsx', N'c:\Users\Cliente\Desktop\PROYECTO\Proyecto\exports\emisores_20251124_232049.xlsx', N'EXPORTADO', CAST(N'2025-11-24T23:20:49.713' AS DateTime), 1)
GO
SET IDENTITY_INSERT [dbo].[Operaciones] OFF
GO
SET IDENTITY_INSERT [dbo].[Usuarios] ON 
GO
INSERT [dbo].[Usuarios] ([UsuarioID], [NombreCompleto], [CorreoElectronico], [Contrasena], [FechaRegistro], [UltimoAcceso], [Estado]) VALUES (1, N'Yoshiharu', N'yoshiijuma2004@gmail.com', N'$2b$12$acM1K3woowCT.Svm/tR2SO0NP4vqdkicfsmp/vl.7xl4VV7aBiBfi', CAST(N'2025-10-26T20:32:33.460' AS DateTime), CAST(N'2025-11-24T23:15:02.113' AS DateTime), N'Activo')
GO
SET IDENTITY_INSERT [dbo].[Usuarios] OFF
GO
ALTER TABLE [dbo].[Operaciones] ADD  DEFAULT (getdate()) FOR [FechaCreacion]
GO
ALTER TABLE [dbo].[Operaciones]  WITH CHECK ADD FOREIGN KEY([UsuarioID])
REFERENCES [dbo].[Usuarios] ([UsuarioID])
GO
