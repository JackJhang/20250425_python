-- public.最新訊息 definition

-- Drop table

-- DROP TABLE public.最新訊息;

CREATE TABLE public.最新訊息 (
	編號 serial4 NOT NULL,
	主題 text NOT NULL,
	上版日期 date NULL,
	內容 text NULL,
	CONSTRAINT newtable_pk PRIMARY KEY ("編號")
);