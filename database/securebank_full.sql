--
-- PostgreSQL database dump
--

\restrict SaN4vE61BA1Mq3d5dW6pRZ6WQjUJaHjd0aBgYftIAInN4eRXNqcatAJPLEXT3fz

-- Dumped from database version 18.7 (Debian 18.7-1.pgdg13+2)
-- Dumped by pg_dump version 18.7 (Debian 18.7-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts; Type: TABLE; Schema: public; Owner: zaza
--

CREATE TABLE public.accounts (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    account_number character varying(30) NOT NULL,
    currency character(3) DEFAULT 'EUR'::bpchar NOT NULL,
    balance numeric(18,2) DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT positive_balance CHECK ((balance >= (0)::numeric))
);


ALTER TABLE public.accounts OWNER TO zaza;

--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: zaza
--

ALTER TABLE public.accounts ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.accounts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: zaza
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    transaction_id character varying(50),
    event_type character varying(50) NOT NULL,
    details text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO zaza;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: zaza
--

ALTER TABLE public.audit_logs ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: zaza
--

CREATE TABLE public.transactions (
    id bigint NOT NULL,
    transaction_id character varying(50) NOT NULL,
    sender_account_id bigint NOT NULL,
    receiver_account_id bigint NOT NULL,
    amount numeric(18,2) NOT NULL,
    currency character(3) NOT NULL,
    status character varying(30) NOT NULL,
    signature_r character varying(64) NOT NULL,
    signature_s character varying(64) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT different_accounts CHECK ((sender_account_id <> receiver_account_id)),
    CONSTRAINT transactions_amount_check CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.transactions OWNER TO zaza;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: zaza
--

ALTER TABLE public.transactions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: zaza
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    role character varying(20) DEFAULT 'customer'::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO zaza;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: zaza
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: zaza
--

COPY public.accounts (id, user_id, account_number, currency, balance, created_at) FROM stdin;
3	3	BOB-001	EUR	3000.00	2026-11-03 19:06:21.864152+00
5	5	SB-CA0B6C04C19B4FF6	EUR	0.00	2026-11-03 23:32:36.434927+00
6	6	SB-F8963D421438493E	EUR	0.00	2026-11-17 19:59:40.242884+00
2	2	ALICE-001	EUR	6000.00	2026-11-03 19:06:21.864152+00
1	1	BANK-001	EUR	98900.00	2026-11-03 19:06:21.864152+00
4	4	ATTACKER-001	EUR	100.00	2026-11-03 19:06:21.864152+00
7	7	SB-A33AC54A34554C65	EUR	0.00	2026-11-18 16:09:57.970045+00
8	8	SB-E7AF695B2F4C4A52	EUR	0.00	2026-11-18 16:11:09.258413+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: zaza
--

COPY public.audit_logs (id, transaction_id, event_type, details, created_at) FROM stdin;
1	TX-9FBE905FF553	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 19:16:43.686366+00
2	TX-C23824ADFBD6	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 21:03:59.104656+00
3	TX-6612FC7DE4C7	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 21:04:26.119884+00
4	TX-DB9553A6623D	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-04 01:17:34.133028+00
5	TX-7D87C15B5A0E	TRANSFER_COMPLETED	BANK transferred 1000.00 EUR to CHARLIE	2026-11-04 01:18:06.909882+00
6	TX-AC4F761AC639	TRANSFER_COMPLETED	CHARLIE transferred 1000.00 EUR to BANK	2026-11-04 01:20:22.113093+00
7	TX-CD6D45E07A4F	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-17 23:59:23.440525+00
8	TX-C73206845739	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-18 00:05:02.974589+00
9	TX-55A1E7935A2A	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-18 00:05:04.286633+00
10	TX-DD99F59C1718	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-18 00:07:16.522111+00
11	TX-632BE4D5C10F	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-18 00:07:23.763161+00
12	TX-7DD847CA9131	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-18 00:07:24.579268+00
13	TX-55FFC6E83FAD	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ATTACKER	2026-11-18 00:08:16.619962+00
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: zaza
--

COPY public.transactions (id, transaction_id, sender_account_id, receiver_account_id, amount, currency, status, signature_r, signature_s, created_at) FROM stdin;
1	TX-9FBE905FF553	1	2	100.00	EUR	COMPLETED	5bacc6344038a53d1ffed30b1546e8b9b7b3fecbf785dc99e232754ba075a04a	82ca67322fbb144f92aabbe40f8f9ae471b1ae42ef193ef12ccba03a2596fd6f	2026-11-03 19:16:43.686366+00
2	TX-C23824ADFBD6	1	2	100.00	EUR	COMPLETED	74d1317f0907fd3c9587f9a073de9120aec5c8746319c18038593d29bb7b9caf	a1b3dbfd4c2b1da27d6193cb89a6d198496c571703f5727dee0847e809b6cf8a	2026-11-03 21:03:59.104656+00
3	TX-6612FC7DE4C7	1	2	100.00	EUR	COMPLETED	f9790b527d825e6b7205e93cf26bff93a850d591390176b942cd46ba78fd175c	6bb5522e4562ebffba1b535fe463c6dc787418bbf83c627ca145c2083ee6eece	2026-11-03 21:04:26.119884+00
4	TX-DB9553A6623D	1	2	100.00	EUR	COMPLETED	81a80a9ef3e533ad1c295bcb7e99ccbb1df40d353bd78bdb76d610719c6e23bf	58d75c1324ce5bbd57112063aa461913dadeb4d6de1881c2e31ba555d9058b4a	2026-11-04 01:17:34.133028+00
5	TX-7D87C15B5A0E	1	5	1000.00	EUR	COMPLETED	59a7424e5eefe4cde8ebfbb313ab3fa33b07478a40dd9285c53b4f3644d80655	5fd7e0308bce5159eca881888d7fa9c4344791dbb98d772961624cce01993ae5	2026-11-04 01:18:06.909882+00
6	TX-AC4F761AC639	5	1	1000.00	EUR	COMPLETED	573a9f52aae7f0fe9188c335d68f5d7ce88ecdc31ada46119d36ff0056f8d369	bda740fc86b270cbec32b91c8a28e2c36d9fcbfbe40f93ec18a467d5a3dad6a1	2026-11-04 01:20:22.113093+00
7	TX-CD6D45E07A4F	1	2	100.00	EUR	COMPLETED	86c4c804fc5c361f403b98cd78affd152208217c8cf05e0380ebbfe688709396	a99d182353abf1fe03a8548abdd80053e161e38b21b29c8cb4251ac8f711c2c0	2026-11-17 23:59:23.440525+00
8	TX-C73206845739	1	2	100.00	EUR	COMPLETED	030c25575c0cfd837e0444e5ad57eefb56921b7e4e5c9d9eb70ac807dea06b5f	72fcc6b04249366eb0647ff9a27c1f7119aeb9585e59251b174636d39c847fbc	2026-11-18 00:05:02.974589+00
9	TX-55A1E7935A2A	1	2	100.00	EUR	COMPLETED	c48d668e683d8779e0d637f86aae272cba8138dd4b8975e4fcf311707eab2dea	f24dcd4590b8e629bf04b4f11800c7541b716626a42e80b6c4229234796726da	2026-11-18 00:05:04.286633+00
10	TX-DD99F59C1718	1	2	100.00	EUR	COMPLETED	fb50388f29498d0a93ad25ec4c34037b9d3cc3cca4787eb6fedabe2b3003eac8	71f437fb7b709bbab2f02f2f1841d2d7b96d06d92c9fe7d1bd264682947c367d	2026-11-18 00:07:16.522111+00
11	TX-632BE4D5C10F	1	2	100.00	EUR	COMPLETED	fb50388f29498d0a93ad25ec4c34037b9d3cc3cca4787eb6fedabe2b3003eac8	0f3ec018f25a347cabfc3baf9efd3e3826607660b0af9746564a64af77cb00fd	2026-11-18 00:07:23.763161+00
12	TX-7DD847CA9131	1	2	100.00	EUR	COMPLETED	fb50388f29498d0a93ad25ec4c34037b9d3cc3cca4787eb6fedabe2b3003eac8	90eff9b80ac986ff59614f4b96322af6cb79b4285078e4130c4964b2c108f385	2026-11-18 00:07:24.579268+00
13	TX-55FFC6E83FAD	1	4	100.00	EUR	COMPLETED	a3527b82c88af0d2f8249976547d1f2a692c6ee53eff1feb4c045d0fe800e91f	799db2f1eca91e7b820cf067e54b8efde4e5927113d3716aa7a9c8566495e538	2026-11-18 00:08:16.619962+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: zaza
--

COPY public.users (id, username, password_hash, created_at, is_active, role) FROM stdin;
3	BOB	scrypt:32768:8:1$nIfaPZ5ifnBmjxT5$d7f837111545e27279deb9be79a1cdbb72244bd27f92226af9b7d47756df28b08f98fbe31d89d2114c9c2d6f93461ed8b32892cace050f15da97c32f7c278a43	2026-11-03 19:06:21.864152+00	t	customer
4	ATTACKER	scrypt:32768:8:1$mV0jIKXxP9TEqAGF$98219c648635125695d1263aa7accbf10be13b75a09b1ff9d9e2aa75698fbfd2baeb69c0bf05952d525c7e625dbfb4b7abdd4895f7919c7cee4f405bc43f6373	2026-11-03 19:06:21.864152+00	t	customer
5	CHARLIE	scrypt:32768:8:1$JfqZTZt9SVLnlOaV$3a21112675ed8dd39993b1754402d43d9a3f6c0ccc46bf21d7d6e3b50a1bfac2e9b773d16f59c3e7c652295841132861b8bc2d60b22d3d02d8f252468a14bc8b	2026-11-03 23:32:36.434927+00	t	customer
6	DOG	scrypt:32768:8:1$c2DeVZGlNhN5eyZF$f45329a91faa42be1c948feee5c5e8bbee57c309d51003a5c4bb16ef3015174bd343861239397dfbfa39110a777035a7511c1c25d3932edbfb4336e629b2b53d	2026-11-17 19:59:40.242884+00	t	customer
2	ALICE	scrypt:32768:8:1$XYDE3ZYNNQGqt07G$056bdaa4e9244b192fbf478723584fc6239bb5d4ccfdaa590d3ead46df11aab8a6effaf1bb9d9755ac74c161d073744c02387d2e120083324713519afbc396ec	2026-11-03 19:06:21.864152+00	t	customer
1	BANK	scrypt:32768:8:1$XYDE3ZYNNQGqt07G$056bdaa4e9244b192fbf478723584fc6239bb5d4ccfdaa590d3ead46df11aab8a6effaf1bb9d9755ac74c161d073744c02387d2e120083324713519afbc396ec	2026-11-03 19:06:21.864152+00	t	admin
7	AYOUB_TAHIRI	scrypt:32768:8:1$3QsD0PjQbOdEMjMM$fc2bf1cb0baf55c4bc0b939b64e39299e142fa81b21951bd02a4dc8cd08ebeda0a4e9a998a10c5efaa3d5aa399bd73c4b6dee603745d2c68685038ef9d1bc794	2026-11-18 16:09:57.970045+00	t	customer
8	islam	scrypt:32768:8:1$kfcjvfYkXjkYHFvX$e685db0946549f15764b386ebee9c9535d67247fc9fe9e5a97dc041b57571fcaa3ea10e444955afb3b564c691877ae33c0c8658b9202a434ff2d5944ba7cfa6b	2026-11-18 16:11:09.258413+00	f	customer
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaza
--

SELECT pg_catalog.setval('public.accounts_id_seq', 8, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaza
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 13, true);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaza
--

SELECT pg_catalog.setval('public.transactions_id_seq', 13, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: zaza
--

SELECT pg_catalog.setval('public.users_id_seq', 8, true);


--
-- Name: accounts accounts_account_number_key; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_account_number_key UNIQUE (account_number);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_transaction_id_key; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_transaction_id_key UNIQUE (transaction_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_audit_logs_transaction; Type: INDEX; Schema: public; Owner: zaza
--

CREATE INDEX idx_audit_logs_transaction ON public.audit_logs USING btree (transaction_id);


--
-- Name: idx_transactions_receiver; Type: INDEX; Schema: public; Owner: zaza
--

CREATE INDEX idx_transactions_receiver ON public.transactions USING btree (receiver_account_id);


--
-- Name: idx_transactions_sender; Type: INDEX; Schema: public; Owner: zaza
--

CREATE INDEX idx_transactions_sender ON public.transactions USING btree (sender_account_id);


--
-- Name: accounts accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: transactions transactions_receiver_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_receiver_account_id_fkey FOREIGN KEY (receiver_account_id) REFERENCES public.accounts(id);


--
-- Name: transactions transactions_sender_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: zaza
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_sender_account_id_fkey FOREIGN KEY (sender_account_id) REFERENCES public.accounts(id);


--
-- PostgreSQL database dump complete
--

\unrestrict SaN4vE61BA1Mq3d5dW6pRZ6WQjUJaHjd0aBgYftIAInN4eRXNqcatAJPLEXT3fz

