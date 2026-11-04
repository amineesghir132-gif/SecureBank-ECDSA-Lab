--
-- PostgreSQL database dump
--

\restrict KJ57dLmEGn63aln8XxgfVovvSBZ3mlsXzD4pBrHWqegPzHppeBZM0zGLLVYg6wX

-- Dumped from database version 18.6 (Debian 18.6-3)
-- Dumped by pg_dump version 18.6 (Debian 18.6-3)

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
-- Name: accounts; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
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
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id bigint NOT NULL,
    transaction_id character varying(50),
    event_type character varying(50) NOT NULL,
    details text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
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
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
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
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    password_hash text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
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
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.accounts (id, user_id, account_number, currency, balance, created_at) FROM stdin;
3	3	BOB-001	EUR	3000.00	2026-11-03 19:06:21.864152+00
4	4	ATTACKER-001	EUR	0.00	2026-11-03 19:06:21.864152+00
2	2	ALICE-001	EUR	5400.00	2026-11-03 19:06:21.864152+00
5	5	SB-CA0B6C04C19B4FF6	EUR	0.00	2026-11-03 23:32:36.434927+00
1	1	BANK-001	EUR	99600.00	2026-11-03 19:06:21.864152+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_logs (id, transaction_id, event_type, details, created_at) FROM stdin;
1	TX-9FBE905FF553	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 19:16:43.686366+00
2	TX-C23824ADFBD6	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 21:03:59.104656+00
3	TX-6612FC7DE4C7	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-03 21:04:26.119884+00
4	TX-DB9553A6623D	TRANSFER_COMPLETED	BANK transferred 100.00 EUR to ALICE	2026-11-04 01:17:34.133028+00
5	TX-7D87C15B5A0E	TRANSFER_COMPLETED	BANK transferred 1000.00 EUR to CHARLIE	2026-11-04 01:18:06.909882+00
6	TX-AC4F761AC639	TRANSFER_COMPLETED	CHARLIE transferred 1000.00 EUR to BANK	2026-11-04 01:20:22.113093+00
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transactions (id, transaction_id, sender_account_id, receiver_account_id, amount, currency, status, signature_r, signature_s, created_at) FROM stdin;
1	TX-9FBE905FF553	1	2	100.00	EUR	COMPLETED	5bacc6344038a53d1ffed30b1546e8b9b7b3fecbf785dc99e232754ba075a04a	82ca67322fbb144f92aabbe40f8f9ae471b1ae42ef193ef12ccba03a2596fd6f	2026-11-03 19:16:43.686366+00
2	TX-C23824ADFBD6	1	2	100.00	EUR	COMPLETED	74d1317f0907fd3c9587f9a073de9120aec5c8746319c18038593d29bb7b9caf	a1b3dbfd4c2b1da27d6193cb89a6d198496c571703f5727dee0847e809b6cf8a	2026-11-03 21:03:59.104656+00
3	TX-6612FC7DE4C7	1	2	100.00	EUR	COMPLETED	f9790b527d825e6b7205e93cf26bff93a850d591390176b942cd46ba78fd175c	6bb5522e4562ebffba1b535fe463c6dc787418bbf83c627ca145c2083ee6eece	2026-11-03 21:04:26.119884+00
4	TX-DB9553A6623D	1	2	100.00	EUR	COMPLETED	81a80a9ef3e533ad1c295bcb7e99ccbb1df40d353bd78bdb76d610719c6e23bf	58d75c1324ce5bbd57112063aa461913dadeb4d6de1881c2e31ba555d9058b4a	2026-11-04 01:17:34.133028+00
5	TX-7D87C15B5A0E	1	5	1000.00	EUR	COMPLETED	59a7424e5eefe4cde8ebfbb313ab3fa33b07478a40dd9285c53b4f3644d80655	5fd7e0308bce5159eca881888d7fa9c4344791dbb98d772961624cce01993ae5	2026-11-04 01:18:06.909882+00
6	TX-AC4F761AC639	5	1	1000.00	EUR	COMPLETED	573a9f52aae7f0fe9188c335d68f5d7ce88ecdc31ada46119d36ff0056f8d369	bda740fc86b270cbec32b91c8a28e2c36d9fcbfbe40f93ec18a467d5a3dad6a1	2026-11-04 01:20:22.113093+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, created_at) FROM stdin;
2	ALICE	scrypt:32768:8:1$D2JjMaUuJCx0s6lP$06ac677300e566a2177eb5a32d6ccf90d4331be8a99fd5b8c2c7ce87b41516249e31542ad4307a77bb87d4a1583fde74ef2c290bc48b11c62ba35d414981137c	2026-11-03 19:06:21.864152+00
3	BOB	scrypt:32768:8:1$nIfaPZ5ifnBmjxT5$d7f837111545e27279deb9be79a1cdbb72244bd27f92226af9b7d47756df28b08f98fbe31d89d2114c9c2d6f93461ed8b32892cace050f15da97c32f7c278a43	2026-11-03 19:06:21.864152+00
4	ATTACKER	scrypt:32768:8:1$mV0jIKXxP9TEqAGF$98219c648635125695d1263aa7accbf10be13b75a09b1ff9d9e2aa75698fbfd2baeb69c0bf05952d525c7e625dbfb4b7abdd4895f7919c7cee4f405bc43f6373	2026-11-03 19:06:21.864152+00
1	BANK	scrypt:32768:8:1$PuoUmWswERJyoHY1$058e35ebd1119a033b2f6808be6733bcb26e4a4878aa54a9f35457f9278500df82db31af2ee9820b7a5b15c4aa3c7aae3b17417c84ab175c6c42ef6de6291d2f	2026-11-03 19:06:21.864152+00
5	CHARLIE	scrypt:32768:8:1$JfqZTZt9SVLnlOaV$3a21112675ed8dd39993b1754402d43d9a3f6c0ccc46bf21d7d6e3b50a1bfac2e9b773d16f59c3e7c652295841132861b8bc2d60b22d3d02d8f252468a14bc8b	2026-11-03 23:32:36.434927+00
\.


--
-- Name: accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_id_seq', 5, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 6, true);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transactions_id_seq', 6, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- Name: accounts accounts_account_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_account_number_key UNIQUE (account_number);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_transaction_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_transaction_id_key UNIQUE (transaction_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_audit_logs_transaction; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_logs_transaction ON public.audit_logs USING btree (transaction_id);


--
-- Name: idx_transactions_receiver; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_transactions_receiver ON public.transactions USING btree (receiver_account_id);


--
-- Name: idx_transactions_sender; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_transactions_sender ON public.transactions USING btree (sender_account_id);


--
-- Name: accounts accounts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: transactions transactions_receiver_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_receiver_account_id_fkey FOREIGN KEY (receiver_account_id) REFERENCES public.accounts(id);


--
-- Name: transactions transactions_sender_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_sender_account_id_fkey FOREIGN KEY (sender_account_id) REFERENCES public.accounts(id);


--
-- PostgreSQL database dump complete
--

\unrestrict KJ57dLmEGn63aln8XxgfVovvSBZ3mlsXzD4pBrHWqegPzHppeBZM0zGLLVYg6wX

