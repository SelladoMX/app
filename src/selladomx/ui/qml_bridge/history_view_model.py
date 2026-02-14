"""ViewModel for document history with pagination."""

from PySide6.QtCore import QObject, Signal, Slot, Property
from ...api.client import SelladoMXAPIClient
from ...api.exceptions import AuthenticationError, NetworkError


class HistoryViewModel(QObject):
    """ViewModel for document history with pagination."""

    # Signals
    historyLoaded = Signal(list, int)  # items, total_count
    loadingChanged = Signal(bool)
    errorOccurred = Signal(str)
    currentPageChanged = Signal(int)

    def __init__(self, api_client: SelladoMXAPIClient):
        super().__init__()
        self._api_client = api_client
        self._history_items = []
        self._total_count = 0
        self._current_page = 1
        self._page_size = 25
        self._is_loading = False

    @Property(list, notify=historyLoaded)
    def historyItems(self):
        return self._history_items

    @Property(int, notify=historyLoaded)
    def totalCount(self):
        return self._total_count

    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._current_page

    @Property(int, constant=True)
    def pageSize(self):
        return self._page_size

    @Property(int, notify=historyLoaded)
    def totalPages(self):
        if self._total_count == 0:
            return 0
        return (self._total_count + self._page_size - 1) // self._page_size

    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._is_loading

    @Slot()
    def loadHistory(self):
        """Load current page of history."""
        self._is_loading = True
        self.loadingChanged.emit(True)

        try:
            offset = (self._current_page - 1) * self._page_size
            response = self._api_client.get_history(
                limit=self._page_size, offset=offset
            )

            self._history_items = response.get("items", [])
            self._total_count = response.get("total", 0)
            self.historyLoaded.emit(self._history_items, self._total_count)

        except AuthenticationError:
            self.errorOccurred.emit("Token inválido o expirado")
        except NetworkError as e:
            self.errorOccurred.emit(f"Error de red: {e.message}")
        except Exception as e:
            self.errorOccurred.emit(f"Error: {str(e)}")
        finally:
            self._is_loading = False
            self.loadingChanged.emit(False)

    @Slot()
    def nextPage(self):
        """Go to next page."""
        if self._current_page < self.totalPages:
            self._current_page += 1
            self.currentPageChanged.emit(self._current_page)
            self.loadHistory()

    @Slot()
    def previousPage(self):
        """Go to previous page."""
        if self._current_page > 1:
            self._current_page -= 1
            self.currentPageChanged.emit(self._current_page)
            self.loadHistory()

    @Slot(int)
    def goToPage(self, page: int):
        """Go to specific page."""
        if 1 <= page <= self.totalPages:
            self._current_page = page
            self.currentPageChanged.emit(self._current_page)
            self.loadHistory()

    @Slot()
    def refresh(self):
        """Refresh current page."""
        self.loadHistory()
