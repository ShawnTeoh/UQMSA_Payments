# Copyright (C) 2015 Thuan Song Teoh
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Version 1.7
# 3/2/2015

import stripe
from Tkinter import *
import tkMessageBox
import logging
import threading
import time
import textwrap
import sys
import os

class PaymentApp(object):

    def __init__(self,master):
        self._status=(True,'')
        logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s',
                            filename='uqmsa_payment.log',level=logging.INFO)
        self._master=master
        self._master.title('UQMSA Payments')
        # Change this path if required
        self._master.iconbitmap(os.path.join(os.path.dirname(sys.argv[0]),
                                             'logo.ico'))
        self._setup_screen()
        self._setup_widgets()

    def _setup_screen(self):
        ScreenSizeX=root.winfo_screenwidth()
        ScreenSizeY=root.winfo_screenheight()
        ScreenRatio=0.3
        FrameSizeX=int(ScreenSizeX*ScreenRatio)
        FrameSizeY=int(ScreenSizeY*ScreenRatio)
        FramePosX=(ScreenSizeX-FrameSizeX)/2
        FramePosY=(ScreenSizeY-FrameSizeY)/2
        self._master.geometry('%sx%s+%s+%s'%(FrameSizeX,FrameSizeY,
                                             FramePosX,FramePosY))
        self._master.resizable(width=FALSE,height=FALSE)

    def _setup_widgets(self):
        frame_root=Frame(root)
        frame_lbl=Frame(frame_root)
        frame_entry=Frame(frame_root)

        Label(frame_lbl,text='Description').pack(fill=BOTH,expand=1)
        self._entry_desc=Entry(frame_entry)
        self._entry_desc.pack(fill=BOTH,expand=1)

        Label(frame_lbl,text='Email').pack(fill=BOTH,expand=1)
        self._entry_email=Entry(frame_entry)
        self._entry_email.pack(fill=BOTH,expand=1)

        Label(frame_lbl,text='Amount (Dollars)').pack(fill=BOTH,expand=1)
        self._entry_amnt=Entry(frame_entry)
        self._entry_amnt.pack(fill=BOTH,expand=1)

        Label(frame_lbl,text='Token').pack(fill=BOTH,expand=1)
        self._entry_tkn=Entry(frame_entry)
        self._entry_tkn.pack(fill=BOTH,expand=1)

        Label(frame_lbl,text='API Key').pack(fill=BOTH,expand=1)
        self._entry_api=Entry(frame_entry)
        self._entry_api.pack(fill=BOTH,expand=1)

        frame_lbl.pack(fill=BOTH,expand=1,side=LEFT)
        frame_entry.pack(fill=BOTH,expand=1,side=LEFT)
        frame_root.pack(fill=BOTH,expand=1)

        self._btn=Button(root,text='Submit',command=self._send)
        self._btn.pack()

        self._lbl_status=Label(root)
        self._lbl_status.pack(fill=BOTH,expand=1)

    def _send(self):
        check=self._verify()

        if (not check[0]):
            tkMessageBox.showerror('Error',check[1])
        else:
            amnt_dlr=self._entry_amnt.get().strip()
            if tkMessageBox.askyesno('Submit','Charge this person with $' +
                                     amnt_dlr + '?'):
                desc=self._entry_desc.get().strip()
                email=self._entry_email.get().strip()
                amnt=int(round(float(amnt_dlr)*100))
                tkn=self._entry_tkn.get().strip()
                stripe.api_key=self._entry_api.get().strip()

                self._toggle('disabled')
                t1=threading.Thread(target=self._query,args=(desc,email,amnt,tkn))
                t1.start()
                t2=threading.Thread(target=self._check_query,args=(t1,))
                t2.start()
            else:
                logging.info('Transaction of $%s cancelled',amnt_dlr)
                logging.info('------------------')

    def _query(self,desc,email,amnt,tkn):
        try:
            logging.info('Charging %d cents for %s',amnt,desc)
            charge=stripe.Charge.create(amount=amnt,
                                        currency='aud',
                                        card=tkn,
                                        description=desc,
                                        receipt_email=email)
            logging.info('Success!')
            logging.info('------------------')
            self._status=(True,'')
        except Exception, e:
            logging.error(str(e))
            logging.error('------------------')
            self._status=(False,textwrap.fill(str(e),50))

    def _check_query(self,t):
        t.join()
        self._toggle('normal')
        if (self._status[0]):
            self._lbl_status.configure(fg='blue',text='Success!')
            self._entry_desc.delete(0,END)
            self._entry_email.delete(0,END)
            self._entry_amnt.delete(0,END)
            self._entry_tkn.delete(0,END)
        else:
            self._lbl_status.configure(fg='red',text=self._status[1])

    def _toggle(self,stat):
        if (stat == 'disabled'):
            txt='Please wait...'
        else:
            txt='Submit'
        self._entry_desc.configure(state=stat)
        self._entry_email.configure(state=stat)
        self._entry_amnt.configure(state=stat)
        self._entry_tkn.configure(state=stat)
        self._entry_api.configure(state=stat)
        self._btn.configure(state=stat,text=txt)

    def _verify(self):
        status=True
        msg=''

        if (self._entry_desc.get().strip() == ''):
            status=False
            msg='Please enter a short description'
        elif (self._entry_email.get().strip() == ''):
            status=False
            msg='Please enter email address of payer'
        elif (self._entry_amnt.get().strip() == '' or
              not self._is_num(self._entry_amnt.get().strip())):
            status=False
            msg='Please enter a valid amount, minimum is 50 cents'
        elif (self._entry_tkn.get().strip() == ''):
            status=False
            msg='Please enter the token'
        elif (self._entry_api.get().strip() == ''):
            status=False
            msg='Please enter the API key'

        return status,msg

    def _is_num(self,num):
        try:
            num=float(num)
            if (num >= 0.5):
                return True
            else:
                return False
        except ValueError:
            return False

root=Tk()
PaymentApp(root)
root.mainloop()
