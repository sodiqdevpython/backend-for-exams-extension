from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Subject
from difflib import SequenceMatcher
import re


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\'"`“‘’”«»]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio() * 100


class FindBestMatchAPIView(APIView):
    def post(self, request, *args, **kwargs):
        query_key = request.data.get('key', '')

        if not query_key:
            return Response({'error': 'Key not provided'}, status=status.HTTP_400_BAD_REQUEST)

        query_key = clean_text(query_key)

        best_match = None
        highest_similarity = 0

        for subject in Subject.objects.all():
            cleaned_key = clean_text(subject.key)
            similarity = get_similarity(query_key, cleaned_key)

            # 60% va undan yuqori o'xshashlikni tekshirish
            if similarity > 60 and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = subject

        if best_match:
            return Response({
                'value': best_match.value,
                'similarity': highest_similarity
            })
        else:
            return Response({'error': 'No matching key found'})


# Bu qism test uchun

import subprocess
import time

class Elog:
    def run_powershell(self, cmd: str) -> str:
        """
        PowerShell buyrug‘ini ishga tushirib, natijani matn ko‘rinishida qaytaradi.
        """
        process = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, encoding="utf-8", shell=True
        )
        
        if process.returncode == 0:
            return process.stdout.strip()
        else:
            return process.stderr.strip()

    def get_all_event_logs(self) -> str:
        """
        Barcha eski uslubdagi Windows event loglarining umumiy ma'lumotlarini chiqaradi.
        """
        cmd = 'Get-EventLog -List | Out-String'
        return self.run_powershell(cmd)

    def get_event_logs(self, log_name: str, limit: int = 10) -> str:
        """
        Eski uslubdagi event loglardan oxirgi N ta yozuvni chiqaradi.
        """
        cmd = f'Get-EventLog -LogName {log_name} -Newest {limit} | Out-String'
        return self.run_powershell(cmd)

    def get_win_event_logs(self, log_name: str, limit: int = 10) -> str:
        """
        Yangi uslubdagi WinEvent loglarini chiqaradi. Avval log nomi mavjudligini tekshiradi.
        """

        cmd = f'Get-WinEvent -LogName "{log_name}" -MaxEvents {limit} | Out-String'
        return self.run_powershell(cmd)

    def get_security_logs(self, limit: int = 10) -> str:
        return self.get_event_logs('Security', limit)

    def get_application_logs(self, limit: int = 10) -> str:
        return self.get_event_logs('Application', limit)

    def get_system_logs(self, limit: int = 10) -> str:
        return self.get_event_logs('System', limit)

    def get_firewall_logs(self, limit: int = 10) -> str:
        return self.get_win_event_logs(
            "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall",
            limit
        )

    def get_task_scheduler_logs(self, limit: int = 10) -> str:
        return self.get_win_event_logs(
            "Microsoft-Windows-TaskScheduler/Operational",
            limit
        )

    def get_powershell_logs(self, limit: int = 10) -> str:
        return self.get_win_event_logs(
            "Microsoft-Windows-PowerShell/Operational",
            limit
        )

    def get_windows_defender_logs(self, limit: int = 10) -> str:
        return self.get_win_event_logs(
            "Microsoft-Windows-Windows Defender/Operational",
            limit
        )

    def get_sysmon_logs(self, limit: int = 10) -> str:
        """
        Sysmon loglarini to‘liq tafsilotlari bilan chiqaradi.
        """
        return self.run_powershell(
            f'Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents {limit} | Format-List *'
        )

    def get_wmi_logs(self, limit: int = 10) -> str:
        return self.get_win_event_logs(
            "Microsoft-Windows-WMI-Activity/Operational",
            limit
        )

    def monitor_sysmon_logs(self, limit: int = 10, delay:int=2):
        print("🟢 Sysmon loglarini kuzatish boshlandi... (To‘xtatish: Ctrl + C)")
        try:
            while True:
                powershell_cmd = (
                    f'Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" '
                    f'-MaxEvents {limit} | Format-List *'
                )
                process = subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", powershell_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8"
                )
                output, error = process.communicate()

                if output:
                    print(output.strip())
                if error:
                    print(f"⚠️ Xatolik: {error.strip()}")

                time.sleep(delay)
        except KeyboardInterrupt:
            print("\n🔴 Monitoring to‘xtatildi.")
