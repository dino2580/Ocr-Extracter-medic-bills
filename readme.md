Activate venv
pip install -r requirements.txt
exceute this command -uvicorn main:app --reload --port 3000
http://localhost:3000/step1/extract
http://localhost:3000/step2/normalize
http://localhost:3000/step3/classify
http://localhost:3000/step4/finalize
Req Type-Post
Input-file-file(for ocr),text-text(already available text)





example usage
http://localhost:3000/step1/extract
Input-image of medical report
Res-
{
	"raw_tokens": [
		{
			"label": "total_bill",
			"raw": "214.00",
			"keyword": "total amount",
			"source_string": "Total Amount : 214.00 oo ssessSsssss",
			"source": "ocr"
		},
		{
			"label": "discount",
			"raw": "13.64",
			"keyword": "dis amount",
			"source_string": "f Dis Amount : 13.64 By Cash Two Hu",
			"source": "ocr"
		},
		{
			"label": "total_paid",
			"raw": "200.36",
			"keyword": "net amount",
			"source_string": "y Net Amount : 200.36 GST is include",
			"source": "ocr"
		},
		{
			"label": "total_paid",
			"raw": "200.00",
			"keyword": "paid amount",
			"source_string": "t Paid Amount: 200.00 Medicine can b",
			"source": "ocr"
		},
		{
			"label": "total_due",
			"raw": "0",
			"keyword": "balance amount",
			"source_string": "alance Amount: 0 Dr, Shae Noell",
			"source": "ocr"
		}
	],
	"currency_hint": "INR",
	"confidence": 0.95,
	"sources_used": [
		"ocr"
	]
}


2 http://localhost:3000/step1/extract
Input -file or text or both
Output-{
	"raw_tokens": [
		{
			"label": "total_bill",
			"raw": "214.00",
			"keyword": "total amount",
			"source_string": "",
			"source": "both"
		},
		{
			"label": "total_paid",
			"raw": "200.00",
			"keyword": "paid amount",
			"source_string": "",
			"source": "both"
		},
		{
			"label": "total_paid",
			"raw": "200.36",
			"keyword": "net amount",
			"source_string": "RA",
			"source": "both"
		},
		{
			"label": "total_due",
			"raw": "0",
			"keyword": "balance amount",
			"source_string": "2022 Age/ Sex     20 Years2/Mal",
			"source": "both"
		},
		{
			"label": "discount",
			"raw": "13.64",
			"keyword": "dis amount",
			"source_string": "f Dis Amount : 13.64 By Cash Two Hu",
			"source": "ocr"
		}
	],
	"currency_hint": "INR",
	"confidence": 0.95,
	"sources_used": [
		"ocr",
		"text"
	]
}

Text used-(      Ujala Cygnus          HtALTHCAR           Amr                    stRVICts                                                          UJALA CYGNUS CENTRAL HOSPITAL               0jola r e p                             collaborat en)          (A Unit of SSGR Hospital & Research Centre Pvt. Ltd.)                       Kaladhungi Road, Tiraha, Near Gas Godam, Kusumkhera, Haldwani, Uttarakhand                                               05946260287/288, 8193812812       DL.NO. : UA-NAI-121461GST NO :05AAECC5494P1Z3                                                  Haldwani                                                       UA-NAI-121462                                                                     INVOICE/RECEIPT Loc Mr No.   1255313 Patient Name NEERAJ BORA                                                                                                             Bill Date           30/03/2022 Age/ Sex     20 Years2/Male                                                                                                             Bill No             :21047581 Dr.Name      DR. SHALABH ARORA                                                                                                            Dr. Name 2: Address             HALDWANI Sr. No.       Medicine Name                                   Qty      Batch No.                                                                              Total                                                                                                           Expiry                             Mrp 1          MUPIKEM OINT SGM                                           121012                              30/09/2022                   140.00                 130.06 2          CLOCIP DUST POw.75GM                               1       KC21290                             31/05/2024                    74.00                   70.3 PayMode: cash                                Card No:                                                                            Total Amount                214.00Received with thanks an amount of                                                                                                                              13.64                                                                                                                                  DisAmountBy Cash   Two Hundred rupees only                                                                                                  Net Amount:                200.36GST is included in Total Amount                                                                                                    Paid Amount                200.00Medicine can be returned only with in 7 days.                                                                                  Dr. Shaábh Arora                                                                                                     A                             Balance Amount:                 0                                                  (WISH YOU A      SPEEDY RECOVERY) , D.M.UK,                                                                                           (Delhi)                                                                                              ECMO                                                                                      DMC     Regd.   No.- 78367                                                                                                                     &   HEART                                                                                                                                               (Pharmacist)                                                                                        HOSPITAL       TRAUMA                                                                            C E N T RC                                                                                     AALR E C E N T R E , H A L D W A N I)



3.
 http://localhost:3000/step2/normalize
Input-file and text


Res-
{
	"normalized_amounts": [
		{
			"label": "total_bill",
			"value": 214.0,
			"source": "both",
			"keyword": "total amount",
			"source_string": ""
		},
		{
			"label": "total_paid",
			"value": 200.0,
			"source": "both",
			"keyword": "paid amount",
			"source_string": ""
		},
		{
			"label": "total_paid",
			"value": 200.36,
			"source": "both",
			"keyword": "net amount",
			"source_string": "RA"
		},
		{
			"label": "total_due",
			"value": 0.0,
			"source": "both",
			"keyword": "balance amount",
			"source_string": "2022 Age/ Sex     20 Years2/Mal"
		},
		{
			"label": "discount",
			"value": 13.64,
			"source": "ocr",
			"keyword": "dis amount",
			"source_string": "f Dis Amount : 13.64 By Cash Two Hu"
		}
	],
	"normalization_confidence": 1.0
}



4.  http://localhost:3000/step3/classify
Input-file or text or both

Res-
{
	"amounts": [
		{
			"type": "total_bill",
			"value": 214.0
		},
		{
			"type": "total_paid",
			"value": 200.36
		},
		{
			"type": "total_due",
			"value": 0.0
		},
		{
			"type": "discount",
			"raw_value": 13.64,
			"discount_value": 13.64,
			"discount_percent": 6.37
		}
	],
	"confidence": 1.0
}


5.http://localhost:3000/step4/finalize
Input -file or text or both
Res-
{
	"currency": "INR",
	"amounts": [
		{
			"type": "total_bill",
			"value": 214.0,
			"source": "text: ''"
		},
		{
			"type": "total_paid",
			"value": 200.36,
			"source": "text: ''"
		},
		{
			"type": "total_due",
			"value": 0.0,
			"source": "text: '2022 Age/ Sex     20 Years2/Mal'"
		},
		{
			"type": "discount_value",
			"value": 13.64,
			"source": "text: 'f Dis Amount : 13.64 By Cash Two Hu'"
		},
		{
			"type": "discount_percent",
			"value": 6.37,
			"source": "text: 'f Dis Amount : 13.64 By Cash Two Hu'"
		}
	],
	"status": "ok"
}





